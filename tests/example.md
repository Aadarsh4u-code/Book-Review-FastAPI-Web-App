# ========================================
# SIMPLE USAGE - Just import and use
# ========================================

# ========================================
# Example 1: Basic Logging in Services
# ========================================
# app/services/book_service.py

from app.core.logger import logger  # Main logger for general app logs


class BookService:
    def __init__(self, session):
        self.session = session

    async def create_book(self, book_data: dict):
        # Info level - general information
        logger.info(f"Creating book: {book_data.get('title')}")

        try:
            new_book = Book(**book_data)
            self.session.add(new_book)
            await self.session.commit()

            # Success message
            logger.info(f"✅ Book created: {new_book.title} - ID: {new_book.id}")
            return new_book

        except Exception as e:
            # Error with exception details
            logger.error(f"❌ Failed to create book: {book_data.get('title')}", exc_info=True)
            raise


# ========================================
# Example 2: Database Logging
# ========================================
# app/services/user_service.py

from app.core.logger import db_logger  # Database-specific logger


class UserService:
    async def get_user_by_email(self, email: str):
        # Use db_logger for database operations
        db_logger.debug(f"Querying user by email: {email}")

        try:
            result = await self.session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if user:
                db_logger.info(f"User found: {email}")
            else:
                db_logger.warning(f"User not found: {email}")

            return user

        except Exception as e:
            db_logger.error(f"Database error querying user: {email}", exc_info=True)
            raise


# ========================================
# Example 3: Using Helper Functions
# ========================================
# app/services/order_service.py

from app.core.logger import (
    logger,  # General logger
    log_exception,  # For structured exception logging
    log_database_query,  # For database operation logging
    log_with_context  # For logging with extra context
)
import time


class OrderService:
    async def create_order(self, order_data: dict):
        logger.info("Processing new order")

        start_time = time.time()
        try:
            new_order = Order(**order_data)
            self.session.add(new_order)
            await self.session.commit()

            duration = time.time() - start_time

            # Log database operation with timing
            log_database_query(
                operation="INSERT",
                table="orders",
                duration=duration,
                order_id=new_order.id,
                total_amount=order_data.get('total')
            )

            # Log with extra context
            log_with_context(
                "info",
                f"Order created successfully",
                order_id=new_order.id,
                user_id=order_data.get('user_id'),
                items_count=len(order_data.get('items', [])),
                duration_ms=round(duration * 1000, 2)
            )

            return new_order

        except Exception as e:
            # Structured exception logging with context
            log_exception(
                e,
                context="create_order",
                order_data=order_data,
                user_id=order_data.get('user_id')
            )
            raise


# ========================================
# Example 4: Router/Endpoint Logging
# ========================================
# app/routers/book_router.py

from fastapi import APIRouter, HTTPException, status, Path
from app.core.logger import logger

book_router = APIRouter()


@book_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, service: BookServiceDep):
    logger.info(f"API endpoint hit: POST /books - Title: {book.title}")

    try:
        result = await service.create_book(book.model_dump())
        logger.info(f"Book creation successful via API: {result.id}")
        return result

    except ValueError as e:
        logger.warning(f"Validation error in create_book: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error in create_book endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@book_router.get("/{book_id}")
async def get_book(book_id: int = Path(..., gt=0), service: BookServiceDep):
    logger.debug(f"GET /books/{book_id} requested")

    book = await service.get_book(book_id)

    if not book:
        logger.warning(f"Book not found: ID {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(..., gt=0), service: BookServiceDep):
    logger.info(f"Delete request for book ID: {book_id}")

    success = await service.delete_book(book_id)

    if not success:
        logger.warning(f"Attempted to delete non-existent book: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")

    logger.info(f"Book {book_id} deleted successfully")
    return None


# ========================================
# Example 5: Different Log Levels
# ========================================
# app/services/payment_service.py

from app.core.logger import logger


class PaymentService:
    async def process_payment(self, payment_data: dict):
        # DEBUG - Detailed information for debugging
        logger.debug(f"Payment data received: {payment_data.keys()}")

        # INFO - General information about normal operation
        logger.info(f"Processing payment for order: {payment_data['order_id']}")

        # WARNING - Something unexpected but not an error
        if payment_data['amount'] > 10000:
            logger.warning(f"Large payment detected: ${payment_data['amount']}")

        try:
            result = await self.charge_card(payment_data)
            logger.info(f"✅ Payment successful: Transaction ID {result['transaction_id']}")
            return result

        except InsufficientFundsError as e:
            # ERROR - Error occurred but was handled
            logger.error(f"Payment failed - Insufficient funds: Order {payment_data['order_id']}")
            raise

        except Exception as e:
            # CRITICAL - Serious error that needs immediate attention
            logger.critical(
                f"CRITICAL: Payment processing failure - Order {payment_data['order_id']}",
                exc_info=True
            )
            raise


# ========================================
# Example 6: Authentication/Security Logging
# ========================================
# app/services/auth_service.py

from app.core.logger import logger


class AuthService:
    async def login(self, email: str, password: str, ip_address: str):
        logger.info(f"Login attempt for: {email} from IP: {ip_address}")

        user = await self.get_user_by_email(email)

        if not user:
            # Security: Log failed login attempts
            logger.warning(
                f"⚠️  Failed login - User not found: {email} from {ip_address}",
                extra={
                    "extra_data": {
                        "event_type": "failed_login",
                        "reason": "user_not_found",
                        "email": email,
                        "ip_address": ip_address
                    }
                }
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not self.verify_password(password, user.password_hash):
            logger.warning(
                f"⚠️  Failed login - Invalid password for: {email} from {ip_address}",
                extra={
                    "extra_data": {
                        "event_type": "failed_login",
                        "reason": "invalid_password",
                        "user_id": user.id,
                        "ip_address": ip_address
                    }
                }
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Successful login
        logger.info(
            f"✅ Successful login: {email} from {ip_address}",
            extra={
                "extra_data": {
                    "event_type": "successful_login",
                    "user_id": user.id,
                    "ip_address": ip_address
                }
            }
        )

        return user


# ========================================
# Example 7: Background Tasks/Jobs
# ========================================
# app/tasks/email_task.py

from app.core.logger import logger


async def send_welcome_email(user_id: int, email: str):
    logger.info(f"📧 Background task started: Send welcome email to {email}")

    try:
        # Your email sending logic
        await email_service.send(
            to=email,
            subject="Welcome!",
            template="welcome"
        )

        logger.info(f"✅ Welcome email sent successfully to {email}")

    except Exception as e:
        logger.error(
            f"❌ Failed to send welcome email to {email}",
            exc_info=True,
            extra={
                "extra_data": {
                    "task": "send_welcome_email",
                    "user_id": user_id,
                    "email": email
                }
            }
        )


# ========================================
# Example 8: Custom Context Logging
# ========================================
# app/services/analytics_service.py

from app.core.logger import log_with_context


class AnalyticsService:
    def track_event(self, event_name: str, user_id: int, properties: dict):
        # Log with rich context for analytics
        log_with_context(
            "info",
            f"Event tracked: {event_name}",
            event_type="analytics",
            event_name=event_name,
            user_id=user_id,
            properties=properties,
            timestamp=time.time()
        )


# ========================================
# Example 9: Exception Handling Patterns
# ========================================
# app/services/file_service.py

from app.core.logger import logger, log_exception


class FileService:
    async def upload_file(self, file_data: bytes, filename: str):
        logger.info(f"Uploading file: {filename} ({len(file_data)} bytes)")

        try:
            # Validation
            if len(file_data) > 10_000_000:  # 10MB
                logger.warning(f"File too large: {filename} - {len(file_data)} bytes")
                raise ValueError("File size exceeds 10MB limit")

            # Process upload
            file_path = await self.save_to_storage(file_data, filename)
            logger.info(f"✅ File uploaded successfully: {filename} -> {file_path}")
            return file_path

        except ValueError as e:
            # Expected error - log as warning
            logger.warning(f"File upload validation failed: {filename} - {e}")
            raise

        except IOError as e:
            # IO error - log with full context
            log_exception(
                e,
                context="file_upload_io_error",
                filename=filename,
                file_size=len(file_data)
            )
            raise

        except Exception as e:
            # Unexpected error - log with full details
            log_exception(
                e,
                context="file_upload_unexpected_error",
                filename=filename,
                file_size=len(file_data)
            )
            raise


# ========================================
# SUMMARY: What to use when
# ========================================

"""
1. GENERAL APP LOGS:
   from app.core.logger import logger
   - Use for: API endpoints, services, business logic
   - Levels: debug, info, warning, error, critical

2. DATABASE LOGS:
   from app.core.logger import db_logger
   - Use for: Database queries, connections, transactions
   - Goes to: database.log file

3. EXCEPTION LOGGING:
   from app.core.logger import log_exception
   - Use for: Catching and logging exceptions with context
   - Automatically includes: traceback, exception type, custom context

4. DATABASE OPERATIONS:
   from app.core.logger import log_database_query
   - Use for: Logging DB operations with timing
   - Includes: operation type, table name, duration, custom fields

5. CONTEXTUAL LOGGING:
   from app.core.logger import log_with_context
   - Use for: Logging with extra structured data
   - Good for: Analytics, audit trails, debugging

LOG LEVELS (when to use):
- DEBUG: Detailed debugging information (dev only)
- INFO: General informational messages (normal operation)
- WARNING: Something unexpected but not an error
- ERROR: Error occurred, but application continues
- CRITICAL: Serious error, may cause application failure
"""