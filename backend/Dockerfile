FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

# Em produção (ENVIRONMENT != development) as dependências de dev (pytest etc.)
# ficam de fora da imagem. Para build de dev, sobrescreva com:
#   poetry install --no-root
ARG INSTALL_DEV=false
RUN poetry config virtualenvs.create false \
 && if [ "$INSTALL_DEV" = "true" ]; then \
      poetry install --no-root; \
    else \
      poetry install --no-root --only main; \
    fi

COPY . .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]