# QuickPickr indexer — Cloud Run Job / one-off crawl (not in default compose stack)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/job

WORKDIR /job

COPY apps/indexer/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/indexer/indexer ./indexer
COPY config ./config

ENTRYPOINT ["python", "-m", "indexer"]
