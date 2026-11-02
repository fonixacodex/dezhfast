# framework/application.py
"""Application — bootstrap اپ FastAPI از ماژول‌ها."""

import logging

from fastapi import FastAPI

from framework.container import Container
from framework.lifecycle import Lifecycle
from framework.module import BaseModule

logger = logging.getLogger(__name__)


class Application:
    def __init__(
        self,
        title: str = "Dezh",
        version: str = "0.1.0",
        debug: bool = False,
    ) -> None:
        self.container = Container()
        self.lifecycle = Lifecycle()
        self._modules: list[BaseModule] = []
        self._booted = False
        self.app = FastAPI(
            title=title,
            version=version,
            debug=debug,
            lifespan=self.lifecycle.lifespan,
        )

    def register_module(self, module: BaseModule) -> "Application":
        if self._booted:
            raise RuntimeError("cannot register module after boot()")

        if not module.name:
            logger.warning("module %s has no 'name'", type(module).__name__)

        module.register_di(self.container)
        module.register_routes(self.app)
        self.lifecycle.add_startup(module.on_startup)
        self.lifecycle.add_shutdown(module.on_shutdown)
        self._modules.append(module)

        logger.debug("module registered: %s", module)
        return self

    def boot(self) -> FastAPI:
        if self._booted:
            raise RuntimeError("application already booted")
        self._booted = True
        logger.info(
            "application booted: %s (modules=%d, routes=%d)",
            self.app.title,
            len(self._modules),
            len(self.app.routes),
        )
        return self.app