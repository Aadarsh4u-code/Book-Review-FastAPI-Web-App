from unittest.mock import patch

auth_prefix = "/api/v1/auth"

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