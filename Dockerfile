# Clean-room validation image. The native workflow remains faster for daily work;
# this image verifies that the repository does not depend on host environments.
FROM node:20-bookworm

ENV UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    PYTHONUNBUFFERED=1 \
    NPM_CONFIG_UPDATE_NOTIFIER=false

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl make git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv \
    && uv python install 3.13

WORKDIR /workspace
COPY . .

RUN uv sync --python 3.13 --extra dev --frozen \
    && cd site \
    && npm ci --no-audit --no-fund

CMD ["make", "test-all"]
