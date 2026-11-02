"""ماژول Jobs با ARQ."""
from framework.module import BaseModule


class JobsModule(BaseModule):
    name = "jobs"

    def register_di(self, container) -> None:
        pass

    def register_routes(self, app) -> None:
        from .router import router
        app.include_router(router, prefix="/jobs", tags=["jobs"])
