# Build context must be the repository root.
FROM node:22-alpine AS frontend-build
WORKDIR /workspace
COPY . .
RUN npm ci
RUN npm run --workspace @math-tutor/frontend build

FROM nginx:1.28-alpine AS frontend
COPY apps/math-tutor/deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /workspace/apps/math-tutor/dist /usr/share/nginx/html

FROM python:3.13-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MATH_TUTOR_DB_PATH=/data/math_tutor.sqlite3
WORKDIR /app/apps/math-tutor
COPY apps/math-tutor/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/math-tutor/backend ./backend
RUN mkdir -p /data
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
