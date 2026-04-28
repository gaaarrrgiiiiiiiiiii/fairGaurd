# FairGuard GCP Deployment Guide

## 1. Prerequisites
- Google Cloud Project (`fairguard-prod-7892`)
- `gcloud` CLI installed and authenticated
- Docker installed locally
- Neon PostgreSQL database instance

## 2. Infrastructure Setup
Enable necessary APIs:
```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com iam.googleapis.com
```

Create a Service Account for Cloud Run:
```bash
gcloud iam service-accounts create fairguard-runner --display-name="FairGuard Cloud Run Service Account"
```

## 3. Secret Management
We used Google Secret Manager to securely store credentials:
```bash
# Add Secrets (Avoid trailing newlines)
echo -n "postgresql://..." | gcloud secrets create DATABASE_URL --data-file=-
echo -n "your_jwt_secret" | gcloud secrets create JWT_SECRET --data-file=-
echo -n "AIzaSy..." | gcloud secrets create GEMINI_API_KEY --data-file=-
echo -n "false" | gcloud secrets create FAIRGUARD_DEV_MODE --data-file=-

# Grant Service Account Access
gcloud secrets add-iam-policy-binding DATABASE_URL --member="serviceAccount:fairguard-runner@fairguard-prod-7892.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
# (Repeat for other secrets)
```

## 4. Container Registry Setup
Create a Docker Artifact Registry:
```bash
gcloud artifacts repositories create fairguard-images --repository-format=docker --location=us-central1
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## 5. Backend Deployment
Update `requirements.txt` to include `psycopg2-binary`.
Build and Push Backend Image:
```bash
docker build -t us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/backend:latest ./backend
docker push us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/backend:latest
```

Deploy to Cloud Run:
```bash
gcloud run deploy fairguard-api \
  --image="us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/backend:latest" \
  --region="us-central1" \
  --service-account="fairguard-runner@fairguard-prod-7892.iam.gserviceaccount.com" \
  --set-secrets="DATABASE_URL=DATABASE_URL:latest,JWT_SECRET=JWT_SECRET:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest,FAIRGUARD_DEV_MODE=FAIRGUARD_DEV_MODE:latest" \
  --allow-unauthenticated \
  --memory="2Gi" --cpu="1"
```

## 6. Frontend Deployment
Pass the backend URL as a build argument so Vite can compile it into the static bundle:
```bash
docker build -t us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/frontend:latest --build-arg VITE_API_BASE_URL="https://fairguard-api-207958058488.us-central1.run.app" ./frontend
docker push us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/frontend:latest
```

Deploy Frontend to Cloud Run:
```bash
gcloud run deploy fairguard-frontend \
  --image="us-central1-docker.pkg.dev/fairguard-prod-7892/fairguard-images/frontend:latest" \
  --region="us-central1" \
  --allow-unauthenticated \
  --memory="512Mi"
```

## 7. Post-Deployment Configuration
Update the Backend's CORS policy to allow the newly generated Frontend URL:
```bash
gcloud run services update fairguard-api \
  --region="us-central1" \
  --update-env-vars ALLOWED_ORIGINS="https://fairguard-frontend-207958058488.us-central1.run.app"
```
