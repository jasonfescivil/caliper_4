FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.5
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

# Install Poetry and Tesseract for OCR
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl tesseract-ocr \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove --purge -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition files
COPY pyproject.toml poetry.lock ./
COPY README.md ./

# Regenerate lock file to ensure it matches pyproject.toml
RUN poetry lock --no-update

# Install only production dependencies using the regenerated lock file
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy source code AFTER dependencies are installed to leverage caching
COPY ./src /app/src
COPY ./prompts /app/prompts

# Build the wheel
RUN poetry build --format wheel --no-interaction --no-ansi

# Uninstall previous version just in case pip doesn't overwrite cleanly
RUN poetry run pip uninstall -y caliper || true

# Install the built wheel
RUN poetry run pip install --no-deps dist/*.whl

# --- Verification Steps (Optional but useful for debugging build issues) ---

# RUN echo "--- Checking source cli.py content AFTER copy ---" && \
#     cat /app/src/caliper/cli.py && \
#     echo "--- Finished checking source cli.py ---" || \
#     (echo "!!! Could not cat source cli.py !!!" && exit 1)

# RUN echo "--- Checking installed cli.py content AFTER install ---" && \
#     cat /usr/local/lib/python3.9/site-packages/caliper/cli.py && \
#     echo "--- Finished checking cli.py ---" || \
#     (echo "!!! Could not cat installed cli.py !!!" && exit 1)

# RUN echo "--- Checking if caliper was installed (pip show) ---" && \
#     poetry run pip show caliper && \
#     echo "--- Finished explicit check ---" || \
#     (echo "!!! pip show caliper FAILED after wheel install !!!" && exit 1)

# --- End Verification Steps ---

# No ENTRYPOINT or CMD; managed by docker-compose
