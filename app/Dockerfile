FROM python:3.11

ENV PATH=/venv/bin:$PATH
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN : \
    && python3.11 -m venv /venv \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV PORT=8000
EXPOSE ${PORT}

ENTRYPOINT uvicorn app.app:app --reload