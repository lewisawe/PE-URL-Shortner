FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY . .

EXPOSE 5000

CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
