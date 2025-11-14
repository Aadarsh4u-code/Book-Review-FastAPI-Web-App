from fastapi import APIRouter, HTTPException, status, Depends

from app.auth.dependencies import RefreshTokenDep, AccessTokenDep, AuthServiceDep, get_current_user, get_role_checker_dep
from app.auth.schemas import MeResponse, TokenResponse, TokenPayload, EmailSchema, SignupResponse, PasswordResetRequest, \
    PasswordResetConfirm
from app.core.logger import logger
from app.shared.exception_handlers import UserAlreadyExists, PasswordNotMatch
from app.shared.utils import UserRole
from app.user.dependencies import UserServiceDep
from app.user.models import UserModel
from app.user.schemas import UserCreate, UserLogin
from app.worker.email_tasks import fastmail, create_email_message

auth_router = APIRouter()
role_checker_dep = get_role_checker_dep([UserRole.user, UserRole.admin, UserRole.superadmin])


# Send Email for Account Verification
@auth_router.post("/send-email", status_code=status.HTTP_200_OK)
async def send_email(user_emails: EmailSchema):
    emails = user_emails.email_address
    html = """<h1>Hi this test mail, thanks for using Fastapi-mail</h1> """
    message = create_email_message(
        recipient=emails,
        subject="Welcome Test Mail",
        body=html.strip(),
    )
    await fastmail.send_message(message)
    return {"message": "Email sent successfully."}



# Register User
@auth_router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(form_data: UserCreate, user_service: UserServiceDep, auth_service: AuthServiceDep):
    # Prevent duplicate emails
    if await user_service.check_user_exists(form_data.email):
        raise UserAlreadyExists(details={"email": form_data.email})

    # Create user (adds + flushes, not committed yet)
    new_user = await user_service.create_user(form_data)

    # The session dependency will commit automatically after this function finishes successfully
    # Try sending verification email AFTER commit succeeds
    try:
        await auth_service.send_verification_email(new_user)
    except Exception as exc:
        # Log but don’t fail signup
        logger.error(f"Email sending failed for {new_user.email}: {exc}")

    # Return success message and user
    return SignupResponse(
        message="Account is created! Check your email to verify your account.",
        user=MeResponse.from_user(new_user)
    )


@auth_router.get("/verify-email/{token}", status_code=status.HTTP_200_OK)
async def verify_email(token: str, auth_service: AuthServiceDep):
    return await auth_service.verify_email_token(token)



# Login / generate access + refresh tokens
@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin, auth_service: AuthServiceDep):
    return await auth_service.login(email=credentials.email, password=credentials.password)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(auth_service: AuthServiceDep, token: TokenPayload = RefreshTokenDep):
    return await auth_service.refresh(token.model_dump())


@auth_router.post("/logout")
async def logout(auth_service: AuthServiceDep, token: TokenPayload = AccessTokenDep):
    return await auth_service.logout(token.model_dump())


@auth_router.post("/revoke")
async def revoke_all(auth_service: AuthServiceDep, token: TokenPayload = AccessTokenDep):
    return await auth_service.revoke_all(token.model_dump())


@auth_router.get("/me", response_model=MeResponse, dependencies=[role_checker_dep])
async def get_me(user: UserModel = Depends(get_current_user)):
    return MeResponse.from_user(user)


@auth_router.post("password-reset-request", status_code=status.HTTP_200_OK)
async def password_reset_request(user_email: PasswordResetRequest, auth_service: AuthServiceDep):
    return await auth_service.password_reset(user_email.email)


@auth_router.post("/password-reset-confirm/{token}", status_code=status.HTTP_200_OK)
async def password_reset_request_confirm(token: str, passwords: PasswordResetConfirm, auth_service: AuthServiceDep):
    if passwords.new_password != passwords.confirm_new_password:
        raise PasswordNotMatch(details={"new_password": passwords.new_password})
    return await auth_service.password_reset_confirm(token, passwords)