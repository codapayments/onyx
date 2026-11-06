"""Dagger module: build Onyx app images for Coda ECR / TeamCity.

Mirrors docker-bake.hcl targets used by upstream GHA and Coda Packaging:

    dagger call lint --source=.
    dagger call backend --source=.
    dagger call web --source=.
    dagger call model-server --source=.
    dagger call package --source=.

Pass ``--base-image-registry`` to use the Coda ECR Docker Hub pull-through
cache on TeamCity agents (avoids Hub rate limits), e.g.
``615638762804.dkr.ecr.ap-southeast-1.amazonaws.com/docker-hub``.
"""

from __future__ import annotations

from typing import Annotated

import dagger
from dagger import BuildArg, Ignore, dag, function, object_type

# Keep packaging contexts lean; match bake contexts (backend/, web/).
_EXCLUDE = [
    ".git",
    ".venv",
    "**/.venv",
    "**/node_modules",
    "**/.next",
    "**/__pycache__",
    "**/*.pyc",
    ".dagger/sdk",
    ".dagger/.venv",
    "mobile",
    "desktop",
    "documentation",
    "docs",
    "examples",
    "extensions",
    "widget",
    "terraform-provider-onyx",
]

_DOCKERFILES = (
    "backend/Dockerfile",
    "backend/Dockerfile.model_server",
    "web/Dockerfile",
)


@object_type
class Onyx:
    """Build the three Onyx images Coda ships to sip/sail/onyx-* ECR repos."""

    def _source(
        self, source: Annotated[dagger.Directory, Ignore(_EXCLUDE)]
    ) -> dagger.Directory:
        return source.filter(exclude=_EXCLUDE)

    def _build_args(self, base_image_registry: str) -> list[BuildArg]:
        return [BuildArg("BASE_IMAGE_REGISTRY", base_image_registry)]

    @function
    async def lint(
        self, source: Annotated[dagger.Directory, Ignore(_EXCLUDE)]
    ) -> str:
        """Assert packaging Dockerfiles exist (cheap PR gate)."""
        src = self._source(source)
        for path in _DOCKERFILES:
            # Force resolution; raises if missing.
            await src.file(path).contents()
        return "dockerfiles ok: " + ", ".join(_DOCKERFILES)

    @function
    def backend(
        self,
        source: Annotated[dagger.Directory, Ignore(_EXCLUDE)],
        base_image_registry: str = "docker.io",
    ) -> dagger.Container:
        """Build ``onyx-backend`` (``backend/Dockerfile`` target ``runtime``)."""
        return self._source(source).directory("backend").docker_build(
            dockerfile="Dockerfile",
            target="runtime",
            build_args=self._build_args(base_image_registry),
        )

    @function
    def web(
        self,
        source: Annotated[dagger.Directory, Ignore(_EXCLUDE)],
        base_image_registry: str = "docker.io",
    ) -> dagger.Container:
        """Build ``onyx-web-server`` (``web/Dockerfile``)."""
        return self._source(source).directory("web").docker_build(
            dockerfile="Dockerfile",
            build_args=self._build_args(base_image_registry),
        )

    @function
    def model_server(
        self,
        source: Annotated[dagger.Directory, Ignore(_EXCLUDE)],
        base_image_registry: str = "docker.io",
    ) -> dagger.Container:
        """Build ``onyx-model-server`` (``backend/Dockerfile.model_server``)."""
        return self._source(source).directory("backend").docker_build(
            dockerfile="Dockerfile.model_server",
            build_args=self._build_args(base_image_registry),
        )

    @function
    async def package(
        self,
        source: Annotated[dagger.Directory, Ignore(_EXCLUDE)],
        base_image_registry: str = "docker.io",
    ) -> str:
        """Build backend + web + model-server (Packaging smoke / full gate)."""
        lint_out = await self.lint(source)
        backend = self.backend(source, base_image_registry)
        web = self.web(source, base_image_registry)
        model = self.model_server(source, base_image_registry)
        # Force evaluation of each image build (CLI would otherwise only print types).
        await backend.sync()
        await web.sync()
        await model.sync()
        return (
            f"{lint_out}\n"
            "package ok: backend (runtime), web, model-server"
        )

    @function
    async def ci(
        self,
        source: Annotated[dagger.Directory, Ignore(_EXCLUDE)],
        base_image_registry: str = "docker.io",
    ) -> str:
        """Alias for ``package`` — shared PR / Packaging entrypoint name."""
        return await self.package(source, base_image_registry)
