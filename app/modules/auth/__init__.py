# app/modules/auth/__init__.py
from framework.module import BaseModule


class AuthModule(BaseModule):
    name = "auth"

    def register_di(self, container) -> None:
        """ثبت وابستگی‌های ماژول auth."""
        # اگر AuthService داری، اینجا ثبت کن:
        # from .service import AuthService
        # container.bind("auth_service", lambda c: AuthService(c.resolve("db")))
        pass

    def register_routes(self, app) -> None:
        from .router import router
        app.include_router(router, prefix="/auth", tags=["auth"])