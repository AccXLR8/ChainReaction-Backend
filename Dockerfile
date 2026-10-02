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
RUN pip install --no-cache-dir "git+${CHAIN_REACTION_REPO}@${CHAIN_REACTION_REF}#subdirectory=python-bindings"

COPY . .

RUN pip install --no-cache-dir .[dev]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
