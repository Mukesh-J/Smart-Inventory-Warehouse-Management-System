from fastapi import FastAPI, Request

from fastapi.responses import JSONResponse

from sqlalchemy.exc import OperationalError


def register_exception_handlers(
    app: FastAPI
):

    @app.exception_handler(
        OperationalError
    )
    async def database_error(
        request: Request,
        exc: OperationalError
    ):

        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database is unavailable"
            }
        )