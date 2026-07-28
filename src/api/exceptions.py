from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):

        return JSONResponse(
            status_code=404, content={"success": False, "error": "Resource not found"}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):

        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )
