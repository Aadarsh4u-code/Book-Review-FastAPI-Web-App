import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.core.logger import log_http_request, log_exception



def register_middleware(app: FastAPI):
    """Register middleware"""

    @app.middleware("http")
    async def custom_http_logging(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        status_code = 500 # Default in case of exception

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            # Log any exception with context
            log_exception(exc, context="HTTP Middleware", path=str(request.url))
            raise  # re-raise so FastAPI can handle it
        finally:
            duration = time.perf_counter() - start_time
            log_http_request(
                method=request.method,
                url=str(request.url),
                status_code=status_code,
                duration=duration,
                client_host=request.client.host,
                client_port=request.client.port,
            )
        return response

    # CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # allowed_hosts = ["localhost", "127.0.0.1", "some-cloud-hosted-url", "0.0.0.0"]
    # if os.getenv("TESTING") == "1":
    #     allowed_hosts.append("testserver")

    app.add_middleware(
        TrustedHostMiddleware,
        # allowed_hosts=allowed_hosts,
        allowed_hosts=["localhost", "127.0.0.1", "some-cloud-hosted-url", "0.0.0.0", "testserver"],
    )

