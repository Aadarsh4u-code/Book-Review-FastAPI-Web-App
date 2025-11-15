from unittest.mock import patch

auth_prefix = "/api/v1/auth"

# Test /send-email endpoint
def test_send_email(client):
    with patch("src.auth.routes.send_email_task.delay") as mock_task:
        response = client.post(f"{auth_prefix}/send-email", json={
            "email_address": ["test@example.com"]
        })

        print('*****', response.json())
        assert response.status_code == 200

        assert response.json() == {"message": "Email sent successfully."}

        mock_task.assert_called_once_with(
            recipient_email=["test@example.com"],
            subject="Welcome Test Mail",
            html_body="""<h1>Hi this test mail, thanks for using Fastapi-mail</h1> """
        )


# Test /signup endpoint
def test_signup_success(client, mock_user_service, mock_auth_service):
    mock_user_service.check_user_exists.return_value = False

    # Fake user with real attributes
    import datetime
    from types import SimpleNamespace
    import uuid

    mock_user = SimpleNamespace(
        uid=uuid.uuid4(),
        username="testuser",
        email="new@example.com",
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        role=SimpleNamespace(value="user"),
        books=[]
    )

    mock_user_service.create_user.return_value = mock_user

    response = client.post(f"{auth_prefix}/signup", json={
        "username": "testuser",
        "email": "new@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "secret123",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == "testuser"
    mock_user_service.check_user_exists.assert_called_once_with("new@example.com")
    mock_user_service.create_user.assert_called_once()
    mock_auth_service.send_verification_email.assert_awaited_once_with(mock_user)
