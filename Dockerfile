FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.cargo/bin:${PATH}"

ARG CHAIN_REACTION_REPO=https://github.com/AccXLR8/ChainReaction-Package.git
ARG CHAIN_REACTION_REF=main

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal

RUN pip install --no-cache-dir --upgrade pip maturin
RUN git clone --depth 1 --branch ${CHAIN_REACTION_REF} ${CHAIN_REACTION_REPO} /tmp/chainreaction-engine \
    && cd /tmp/chainreaction-engine \
    && if [ ! -d cli ]; then \
         mkdir -p cli/src \
         && printf '[package]\nname = "cli"\nversion = "0.1.0"\nedition = "2021"\npublish = false\n\n[dependencies]\nengine = { path = "../engine" }\n' > cli/Cargo.toml \
         && printf 'fn main() {}\n' > cli/src/main.rs; \
       fi \
    && cd /tmp/chainreaction-engine/python-bindings \
    && maturin build --release --strip \
    && pip install --no-cache-dir target/wheels/*.whl \
    && rm -rf /tmp/chainreaction-engine

COPY . .

RUN pip install --no-cache-dir .[dev]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
