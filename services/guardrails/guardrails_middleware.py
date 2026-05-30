"""
Guardrails Middleware for ExamGrader API

This middleware intercepts all API requests and responses to apply OPEA guardrails:
- Input validation and PII detection
- Output sanitization
- Content safety checks
"""

import os
import httpx
import logging
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

GUARDRAIL_SERVICE_URL = os.getenv("GUARDRAIL_SERVICE_URL", "http://guardrails:9090")
GUARDRAIL_TIMEOUT = 5.0

class GuardrailsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies OPEA guardrails to all API requests and responses.

    This middleware:
    1. Checks all user inputs for PII and safety issues before processing
    2. Validates AI outputs for safety before returning to users
    3. Logs all security events for audit purposes
    """

    def __init__(self, app, guardrail_url: str = GUARDRAIL_SERVICE_URL):
        super().__init__(app)
        self.guardrail_url = guardrail_url
        self.enabled = os.getenv("GUARDRAILS_ENABLED", "true").lower() == "true"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID", "unknown")

        try:
            if self._should_check_request(request):
                guardrail_result = await self._check_input(request)
                if guardrail_result and guardrail_result.get("action") == "block":
                    logger.warning(
                        f"[Guardrails] Request blocked for request_id={request_id}, "
                        f"risk_categories={guardrail_result.get('risk_categories')}"
                    )
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Content policy violation",
                            "message": "Your input contains prohibited content. Please revise and try again.",
                            "request_id": request_id,
                            "risk_categories": guardrail_result.get("risk_categories", [])
                        }
                    )

            response = await call_next(request)

            if self._should_check_response(request):
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                guardrail_result = await self._check_output(response_body.decode("utf-8"))
                if guardrail_result and guardrail_result.get("action") == "block":
                    logger.warning(
                        f"[Guardrails] Response blocked for request_id={request_id}"
                    )
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": "Output safety violation",
                            "message": "Generated content did not pass safety checks. Please try again.",
                            "request_id": request_id
                        }
                    )

                if guardrail_result and guardrail_result.get("redacted_text"):
                    redacted = guardrail_result["redacted_text"]
                    return Response(
                        content=redacted,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )

            return response

        except Exception as e:
            logger.error(f"[Guardrails] Middleware error: {str(e)}")
            return await call_next(request)

    def _should_check_request(self, request: Request) -> bool:
        """Determine if request should be checked"""
        skip_paths = ["/health", "/docs", "/openapi.json", "/v1/categories"]
        if request.url.path in skip_paths:
            return False
        if request.url.path.startswith("/v1/hash"):
            return False
        return True

    def _should_check_response(self, request: Request) -> bool:
        """Determine if response should be checked"""
        check_paths = ["/v1/grade", "/v1/analyze", "/v1/suggest"]
        return any(request.url.path.startswith(p) for p in check_paths)

    async def _check_input(self, request: Request) -> Optional[Dict[str, Any]]:
        """Send request content to guardrail service for validation"""
        try:
            body = await request.body()
            if not body:
                return None

            text = body.decode("utf-8")

            async with httpx.AsyncClient(timeout=GUARDRAIL_TIMEOUT) as client:
                response = await client.post(
                    f"{self.guardrail_url}/v1/guardrail/input",
                    json={
                        "text": text,
                        "check_pii": True,
                        "check_safety": True,
                        "redact_pii": True,
                        "return_redacted": True
                    }
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except httpx.TimeoutException:
            logger.warning("[Guardrails] Input check timed out, proceeding without check")
            return None
        except Exception as e:
            logger.error(f"[Guardrails] Input check failed: {str(e)}")
            return None

    async def _check_output(self, text: str) -> Optional[Dict[str, Any]]:
        """Send response content to guardrail service for validation"""
        try:
            async with httpx.AsyncClient(timeout=GUARDRAIL_TIMEOUT) as client:
                response = await client.post(
                    f"{self.guardrail_url}/v1/guardrail/output",
                    json={
                        "text": text,
                        "check_pii": True,
                        "check_safety": True,
                        "redact_pii": True,
                        "return_redacted": True
                    }
                )

                if response.status_code == 200:
                    return response.json()
                return None

        except httpx.TimeoutException:
            logger.warning("[Guardrails] Output check timed out, proceeding without check")
            return None
        except Exception as e:
            logger.error(f"[Guardrails] Output check failed: {str(e)}")
            return None


def get_guardrails_client(guardrail_url: str = GUARDRAIL_SERVICE_URL):
    """
    Get a guardrails client for direct API usage.

    Usage:
        from guardrails_middleware import get_guardrails_client

        client = get_guardrails_client()
        result = await client.check_content("Some text to check")
    """
    return GuardrailsClient(guardrail_url)


class GuardrailsClient:
    """Client for interacting with the Guardrails microservice"""

    def __init__(self, base_url: str = GUARDRAIL_SERVICE_URL):
        self.base_url = base_url
        self.timeout = GUARDRAIL_TIMEOUT

    async def check_content(self, text: str) -> Dict[str, Any]:
        """Check content for PII and safety issues"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/guardrail",
                json={
                    "text": text,
                    "check_pii": True,
                    "check_safety": True,
                    "redact_pii": True,
                    "return_redacted": True
                }
            )
            response.raise_for_status()
            return response.json()

    async def check_input(self, text: str) -> Dict[str, Any]:
        """Check user input"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/guardrail/input",
                json={
                    "text": text,
                    "check_pii": True,
                    "check_safety": True,
                    "redact_pii": True,
                    "return_redacted": True
                }
            )
            response.raise_for_status()
            return response.json()

    async def check_output(self, text: str) -> Dict[str, Any]:
        """Check AI-generated output"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/guardrail/output",
                json={
                    "text": text,
                    "check_pii": True,
                    "check_safety": True,
                    "redact_pii": True,
                    "return_redacted": True
                }
            )
            response.raise_for_status()
            return response.json()

    async def batch_check(self, texts: list) -> Dict[str, Any]:
        """Check multiple texts"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/guardrail/batch",
                json={
                    "texts": texts,
                    "check_pii": True,
                    "check_safety": True,
                    "redact_pii": True
                }
            )
            response.raise_for_status()
            return response.json()

    async def generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate integrity hash for data"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/hash",
                json={"data": data}
            )
            response.raise_for_status()
            return response.json()["hash"]

    async def health_check(self) -> bool:
        """Check if guardrail service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False
