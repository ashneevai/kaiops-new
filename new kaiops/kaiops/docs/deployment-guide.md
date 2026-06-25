# Deployment Guide

## Local
- docker compose -f infrastructure/docker/docker-compose.yml up -d
- Run API and Web apps via native dev runtime

## Kubernetes
- Apply namespace first
- Apply secrets
- Apply deployment/service manifests
- Apply ingress and HPA

## Cloud
- Terraform modules exist for AWS, Azure, GCP under infrastructure/terraform
- Integrate with managed PostgreSQL, Redis, and Kafka in production

## Security
- Store secrets in cloud secret manager
- Enforce TLS at ingress and service mesh
- Rotate JWT signing key and OIDC credentials
