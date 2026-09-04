FROM ghcr.io/astral-sh/uv:0.12.9@sha256:8b940d3a9d65bed080436972241af2e21c84b5e8c9193f7014ed71479ee795ff AS uv
FROM python:3.12.14-slim-trixie@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS builder

COPY --from=uv /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12.14-slim-trixie@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea AS runtime

RUN groupadd --system --gid 1001 beanco \
    && useradd --system --uid 1001 --gid beanco --home-dir /app beanco

WORKDIR /app
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV PATH=/app/.venv/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /app/.venv ./.venv
COPY . .

RUN DJANGO_SETTINGS_MODULE=config.settings.base python manage.py collectstatic --noinput \
    && chown -R beanco:beanco /app

USER beanco
EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
