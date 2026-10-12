from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.config import ensure_directories, settings
from app.database import init_db
from app.errors import EchoFlowError

PAGE_MAP = {
    "/": "frontend/index.html",
    "/transcriptions": "frontend/transcriptions.html",
    "/speech-analytics": "frontend/analytics.html",
    "/model-evaluation": "frontend/evaluation.html",
    "/business-insights": "frontend/insights.html",
    "/settings": "frontend/settings.html",
}


def create_app() -> FastAPI:
    ensure_directories()
    init_db()
    application = FastAPI(title=settings.app_name, version="0.1.0")
    application.include_router(api_router, prefix="/api")
    application.mount("/static", StaticFiles(directory="frontend"), name="static")

    @application.exception_handler(EchoFlowError)
    async def handle_echoflow_error(_: Request, exc: EchoFlowError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "code": exc.code},
        )

    @application.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail
        message = detail if isinstance(detail, str) else "The request could not be completed."
        return JSONResponse(status_code=exc.status_code, content={"error": message})

    @application.exception_handler(RequestValidationError)
    async def handle_validation(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "The request was missing required information or used an invalid format."},
        )

    @application.exception_handler(Exception)
    async def handle_unexpected(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred while processing the request."},
        )

    @application.get("/")
    def dashboard_page() -> FileResponse:
        return FileResponse("frontend/index.html")

    @application.get("/transcriptions")
    def transcriptions_page() -> FileResponse:
        return FileResponse("frontend/transcriptions.html")

    @application.get("/speech-analytics")
    def analytics_page() -> FileResponse:
        return FileResponse("frontend/analytics.html")

    @application.get("/model-evaluation")
    def evaluation_page() -> FileResponse:
        return FileResponse("frontend/evaluation.html")

    @application.get("/business-insights")
    def insights_page() -> FileResponse:
        return FileResponse("frontend/insights.html")

    @application.get("/settings")
    def settings_page() -> FileResponse:
        return FileResponse("frontend/settings.html")

    return application


app = create_app()
