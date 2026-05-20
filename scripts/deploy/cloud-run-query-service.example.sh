#!/usr/bin/env bash
# Example: deploy query-service to Cloud Run (adjust PROJECT_ID, REGION, SA).
# Requires: gcloud auth, Artifact Registry repo, Vertex + Secret Manager configured.
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
REGION="${GCP_REGION:-asia-south1}"
SERVICE="quickpickr-query"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/quickpickr/${SERVICE}:latest"

gcloud builds submit . \
  --config cloudbuild-query.yaml \
  --substitutions "_IMAGE=${IMAGE}"

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 20 \
  --cpu 1 \
  --memory 1Gi \
  --timeout 30 \
  --set-env-vars "ENVIRONMENT=prod" \
  --set-secrets "VERTEX_SEARCH_SERVING_CONFIG=VERTEX_SEARCH_SERVING_CONFIG:latest" \
  --service-account "quickpickr-query@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Deployed. Set NEXT_PUBLIC_API_URL to the service URL for the web build."
