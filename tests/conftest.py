import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from src.main import app
from src.db.session import get_db_session
from src.auth.dependencies import get_current_user, get_auth_service, AccessTokenBearer, RefreshTokenBearer
from src.user.dependencies import get_user_service
from src.books.dependencies import get_book_service
from src.reviews.dependencies import get_review_service
from src.tags.dependencies import get_tag_service
from src.db.redis import redis_client


# ============================================================
# 1. GLOBAL MOCK OBJECTS (private variables)
# ============================================================

_mock_db_session = AsyncMock()
_mock_user_service = AsyncMock()
_mock_book_service = AsyncMock()
_mock_review_service = AsyncMock()
_mock_auth_service = AsyncMock()
_mock_tag_service = AsyncMock()

_mock_current_user = MagicMock()
_mock_current_user.uid = uuid.uuid4()
_mock_current_user.email = "test@example.com"
_mock_current_user.role = "admin"
_mock_current_user.is_active = True
_mock_current_user.is_verified = True


# ============================================================
# 2. FIXTURES EXPOSE MOCK OBJECTS (public names)
# ============================================================

@pytest.fixture
def mock_db_session():
    return _mock_db_session


@pytest.fixture
def mock_user_service():
    return _mock_user_service


@pytest.fixture
def mock_book_service():
    return _mock_book_service


@pytest.fixture
def mock_review_service():
    return _mock_review_service


@pytest.fixture
def mock_auth_service():
    return _mock_auth_service


@pytest.fixture
def mock_tag_service():
    return _mock_tag_service


@pytest.fixture
def mock_current_user():
    return _mock_current_user


# ============================================================
# 3. DEPENDENCY OVERRIDES
# ============================================================

# DB Session override
async def override_get_db_session():
    yield _mock_db_session


# Services overrides
async def override_get_user_service():
    return _mock_user_service


async def override_get_book_service():
    return _mock_book_service


async def override_get_review_service():
    return _mock_review_service


async def override_get_auth_service():
    return _mock_auth_service


async def override_get_tag_service():
    return _mock_tag_service


# Auth dependency (skip real JWT validation)
class MockAccessTokenBearer:
    async def __call__(self, *args, **kwargs):
        return {"user": {"email": _mock_current_user.email}, "refresh": False}


class MockRefreshTokenBearer:
    async def __call__(self, *args, **kwargs):
        return {"user": {"email": _mock_current_user.email}, "refresh": True}


# Current user override
async def override_get_current_user():
    return _mock_current_user


# ============================================================
# 4. APPLY ALL OVERRIDES
# ============================================================

app.dependency_overrides[get_db_session] = override_get_db_session
app.dependency_overrides[get_user_service] = override_get_user_service
app.dependency_overrides[get_book_service] = override_get_book_service
app.dependency_overrides[get_review_service] = override_get_review_service
app.dependency_overrides[get_auth_service] = override_get_auth_service
app.dependency_overrides[get_tag_service] = override_get_tag_service

app.dependency_overrides[AccessTokenBearer] = MockAccessTokenBearer()
app.dependency_overrides[RefreshTokenBearer] = MockRefreshTokenBearer()
app.dependency_overrides[get_current_user] = override_get_current_user


# ============================================================
# 5. REDIS MOCKING
# ============================================================

redis_client.init_redis = AsyncMock(return_value=True)
redis_client.close_redis = AsyncMock(return_value=True)
redis_client.is_token_revoked = AsyncMock(return_value=False)


# ============================================================
# 6. TEST CLIENT FIXTURE
# ============================================================

@pytest.fixture
def client():
    return TestClient(app)


# ============================================================
# 7. EXAMPLE DATA FIXTURES (OPTIONAL)
# ============================================================

@pytest.fixture
def fake_user():
    return _mock_current_user


@pytest.fixture
def fake_db():
    return _mock_db_session


@pytest.fixture
def fake_book():
    return {
        "title": "Sample Book",
        "description": "Test description",
        "page_count": 200
    }



# def test_signup_success(client, mock_user_service, mock_auth_service):
#     mock_user_service.check_user_exists.return_value = False
#     mock_user = mock_user_service.create_user.return_value
#     mock_user.email = "new@example.com"
#
#     res = client.post(f"{pre}/signup", json={
#         "email": "new@example.com",
#         "password": "secret123",
#         "full_name": "Test User"
#     })
#
#     assert res.status_code == 201
#     mock_user_service.check_user_exists.assert_called_once_with("new@example.com")
#     mock_user_service.create_user.assert_called_once()



# # 1. GLOBAL MOCK OBJECTS
# mock_db_session = AsyncMock()
# mock_user_service = AsyncMock()
# mock_book_service = AsyncMock()
# mock_review_service = AsyncMock()
# mock_auth_service = AsyncMock()
# mock_tag_service = AsyncMock()
#
#
# mock_current_user = MagicMock()
# mock_current_user.uid = uuid.uuid4()
# mock_current_user.email = "test@example.com"
# mock_current_user.role = "admin"
# mock_current_user.is_active = True
# mock_current_user.is_verified = True
#
#
# # 2. OVERRIDE: DB SESSION
# async def override_get_db_session():
#     yield mock_db_session
#
#
# # 3. OVERRIDE: SERVICES
# async def override_get_user_service():
#     return mock_user_service
#
#
# async def override_get_book_service():
#     return mock_book_service
#
#
# async def override_get_review_service():
#     return mock_review_service
#
#
# async def override_get_auth_service():
#     return mock_auth_service
#
# async def override_get_tag_service():
#     return mock_tag_service
#
#
# # 4. OVERRIDE: Auth Token Bearers (skip real JWT validation)
# class MockAccessTokenBearer:
#     async def __call__(self, *args, **kwargs):
#         return {"user": {"email": mock_current_user.email}, "refresh": False}
#
#
# class MockRefreshTokenBearer:
#     async def __call__(self, *args, **kwargs):
#         return {"user": {"email": mock_current_user.email}, "refresh": True}
#
#
#
# # 5. OVERRIDE: Current User
# async def override_get_current_user():
#     return mock_current_user
#
#
# # 6. OVERRIDE REDIS
# redis_client.init_redis = AsyncMock(return_value=True)
# redis_client.close_redis = AsyncMock(return_value=True)
# redis_client.is_token_revoked = AsyncMock(return_value=False)
#
#
#
# # 7. APPLY ALL DEPENDENCY OVERRIDES
# app.dependency_overrides[get_db_session] = override_get_db_session
# app.dependency_overrides[get_user_service] = override_get_user_service
# app.dependency_overrides[get_book_service] = override_get_book_service
# app.dependency_overrides[get_review_service] = override_get_review_service
# app.dependency_overrides[get_auth_service] = override_get_auth_service
# app.dependency_overrides[get_tag_service] = override_get_tag_service
#
# # IMPORTANT — USE CLASS, NOT INSTANCE
# app.dependency_overrides[AccessTokenBearer] = MockAccessTokenBearer()
# app.dependency_overrides[RefreshTokenBearer] = MockRefreshTokenBearer()
#
# app.dependency_overrides[get_current_user] = override_get_current_user
#
#
# # 8. TEST CLIENT FIXTURE
# @pytest.fixture
# def client():
#     """Test client."""
#     return TestClient(app)
#
# # 9 FIXTURE FOR SERVICES
#
#
# # 10. EXAMPLE DATA FIXTURES (books, users...)
# @pytest.fixture
# def fake_user():
#     return mock_current_user
#
#
# @pytest.fixture
# def fake_db():
#     return mock_db_session
#
#
# @pytest.fixture
# def fake_book():
#     return {"title": "Sample Book", "description": "Test description", "page_count": 200}
#
#
#
#
