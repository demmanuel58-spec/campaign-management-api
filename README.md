# Campaign Management API v1.0

[![Continuous Integration](https://github.com/your-username/campaign-management-api/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/campaign-management-api/actions)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)

A production-oriented FastAPI backend platform designed for managing marketing campaigns, executing task coordination, enforcing Role-Based Access Control (RBAC), and maintaining mutation audit logs.

## Domain Context
Before transitioning into backend engineering, I managed marketing operations across consumer brands—handling multi-team approval pipelines, tight launch deadlines, and client deliverables. Real-world marketing workflows depend on strict state management and auditability. I built this system to translate operational realities into a structured, secure backend engine.

## System Architecture
![Architecture](docs/architecture.png)

```text
  [ Client Application / Postman ]
                 │
                 ▼
         ┌───────────────┐
         │ FastAPI v1    │  <── Request ID Tracing (X-Request-ID) & CORS
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Auth Guard    │  <── OAuth2 + JWT Expiration Checks & RBAC
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ CRUD Services │  <── Single-Transaction Log Mutations & Task Rules
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ SQLAlchemy    │  <── Composite Indexes & Connection Pooling
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │  PostgreSQL   │
         └───────────────┘
