from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse


class CustomSwaggerUI:
    def __init__(
        self,
        app: FastAPI,
        title: str = "Chat Service API",
        swagger_favicon_url: str = "/static/favicon.png",
    ):
        self.app = app
        self.title = title
        self.swagger_favicon_url = swagger_favicon_url

    def setup(self):
        @self.app.get("/swagger/index.html", include_in_schema=False)
        async def custom_swagger_ui() -> HTMLResponse:
            return get_swagger_ui_html(
                openapi_url=self.app.openapi_url,
                title=f"{self.title} - Swagger UI",
                oauth2_redirect_url=self.app.swagger_ui_oauth2_redirect_url,
                swagger_favicon_url=self.swagger_favicon_url,
                swagger_ui_parameters={
                    "syntaxHighlight": {"theme": "obsidian"},
                    "docExpansion": "none",
                    "persistAuthorization": True,
                    "displayRequestDuration": True,
                },
            )

        @self.app.get(self.app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
        async def swagger_ui_redirect():
            return get_swagger_ui_html(
                openapi_url=self.app.openapi_url,
                title=f"{self.title} - OAuth2 Redirect",
            )

        @self.app.get("/redoc", include_in_schema=False)
        async def redoc_ui() -> HTMLResponse:
            return get_redoc_html(
                openapi_url=self.app.openapi_url,
                title=f"{self.title} - ReDoc",
                redoc_favicon_url=self.swagger_favicon_url,
            )
