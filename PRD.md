# Product Requirements Document (PRD)

## Project Title
Scalable Backend System with Integrated Trading Engine (Web + CLI)

---

## 1. Executive Summary

This project is a production-ready backend system integrated with a CLI-based trading bot. It demonstrates scalable API design, secure authentication, modular architecture, and real-world trading API integration.

The system enables users to:
- Register and authenticate securely using JWT
- Perform CRUD operations on tasks
- Execute cryptocurrency trades via Binance Futures Testnet
- Interact through both a web interface (Next.js) and a CLI tool

The project is designed to meet industry standards in backend engineering, including clean architecture, validation, logging, and deployment readiness.

---

## 2. Objectives

### Primary Objectives
- Build a secure and scalable RESTful API
- Implement authentication and role-based access control
- Design a modular backend architecture
- Integrate trading functionality using an external API
- Provide both web and CLI interfaces

### Secondary Objectives
- Implement structured logging
- Ensure robust validation and error handling
- Provide clear API documentation
- Demonstrate scalability and deployment readiness

---

## 3. Target Users

- Backend developer recruiters
- Hiring teams evaluating engineering skills
- Developers testing trading systems
- Students learning backend architecture

---

## 4. System Architecture Overview

- Frontend (Next.js) communicates with the Flask backend API
- Backend processes requests through routes → controllers → services
- Trading module integrates with Binance Testnet
- CLI directly uses the same trading module
- PostgreSQL is used for persistent storage

---

## 5. Technology Stack

### Backend
- Python 3.x
- Flask
- SQLAlchemy
- JWT (authentication)
- bcrypt (password hashing)

### Frontend
- Next.js (React)

### CLI
- argparse / Typer

### Database
- PostgreSQL

### External Integration
- python-binance

### Tooling
- Swagger (API documentation)
- Postman collection
- python-dotenv
- logging module

---

## 6. Project Structure

```
project-root/
backend/
  app.py
  config.py
  extensions.py
  models/
    user_model.py
    task_model.py
    trade_model.py
  routes/
    auth_routes.py
    task_routes.py
    trade_routes.py
  controllers/
    auth_controller.py
    task_controller.py
    trade_controller.py
  services/
    auth_service.py
    task_service.py
    trade_service.py
  trading/
    client.py
    orders.py
    validators.py
    utils.py
  middlewares/
    auth_middleware.py
    role_middleware.py
  utils/
    response.py
    error_handler.py
    logger.py
  schemas/
    auth_schema.py
    task_schema.py
    trade_schema.py
  docs/
    swagger.yaml
cli/
  cli.py
  commands.py
frontend/
  pages/
    index.js
    login.js
    register.js
    dashboard.js
  components/
    TaskForm.js
    TaskList.js
    TradeForm.js
  utils/
    api.js
logs/
  app.log
.env
requirements.txt
package.json
README.md
docker-compose.yml (optional)
```

---

## 7. Functional Requirements

### 7.1 Authentication and Authorization

- User registration
- User login
- Password hashing using bcrypt
- JWT token generation and validation
- Role-based access control (USER and ADMIN)

Access Rules:
- USER → access only own data
- ADMIN → access all data

---

### 7.2 Task Management (CRUD)

Entity: Task

Fields:
- id
- title
- description
- status
- user_id

Endpoints:
- GET /api/v1/tasks
- POST /api/v1/tasks
- PUT /api/v1/tasks/{id}
- DELETE /api/v1/tasks/{id}

---

### 7.3 Trading Module

Features:
- Place MARKET orders
- Place LIMIT orders
- Support BUY and SELL

Inputs:
- symbol (e.g., BTCUSDT)
- side (BUY/SELL)
- type (MARKET/LIMIT)
- quantity
- price (required for LIMIT)

---

### 7.4 CLI Trading Bot

- Accepts input via CLI
- Validates input
- Executes trades via shared module
- Outputs:
  - request summary
  - response details
  - success/failure message

Example:
```
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

---

### 7.5 Trading API

Endpoints:
- POST /api/v1/trades/order
- GET /api/v1/trades/history

Behavior:
- Validate input
- Execute trade
- Store result in database
- Return structured response

---

### 7.6 Logging

- Logs stored in logs/app.log
- Includes:
  - API requests
  - responses
  - errors

Logging levels:
- INFO
- WARNING
- ERROR

---

### 7.7 API Design

- RESTful architecture
- Versioning: /api/v1
- Proper HTTP methods
- Stateless design

Status Codes:
- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Internal Server Error

---

### 7.8 API Documentation

- Swagger UI
- Postman collection

---

### 7.9 Frontend

Pages:
- Register
- Login
- Dashboard

Features:
- JWT handling
- Protected routes
- Task CRUD
- Trade execution form
- API response display

---

## 8. Database Schema

### Users
- id
- email (unique)
- password_hash
- role

### Tasks
- id
- title
- description
- status
- user_id

### Trades
- id
- user_id
- symbol
- side
- type
- quantity
- price
- status
- order_id

Relationships:
- User → Tasks (1:N)
- User → Trades (1:N)

---

## 9. Workflows

### Authentication Flow
1. User registers
2. Password hashed
3. User logs in
4. JWT issued
5. Token used for protected routes

### Trading Flow (Web)
1. User submits order
2. Backend validates input
3. Trading module executes order
4. Response stored in DB
5. Response returned

### Trading Flow (CLI)
1. User inputs command
2. Input validated
3. Order executed
4. Output printed and logged

---

## 10. Security

- Password hashing (bcrypt)
- JWT authentication with expiry
- Input validation and sanitization
- Secure environment variables
- Role-based authorization

---

## 11. Validation and Error Handling

- Schema-based validation
- Centralized error handling
- Structured error responses

Example:
```
{
  "error": "Invalid input",
  "message": "Price is required for LIMIT orders"
}
```

---

## 12. Scalability and Deployment

- Modular architecture
- Separation of concerns
- Environment-based configuration

Future Enhancements:
- Redis caching
- Background jobs (Celery)
- Docker deployment
- Microservices architecture

---

## 13. Testing Strategy

- API testing via Postman
- CLI testing manually
- Edge case validation:
  - invalid inputs
  - API failures
  - authentication errors

---

## 14. Deliverables

- GitHub repository
- Backend APIs
- CLI trading bot
- Frontend UI
- Swagger documentation
- Log files (market + limit orders)
- README with setup and usage

---

## 15. Success Criteria

- RESTful API design
- Secure authentication and RBAC
- Functional CRUD operations
- Successful trading execution on testnet
- Clean, modular codebase
- Proper validation and error handling
- Meaningful logging
- Functional frontend integration
- Clear and complete README

---

## 16. Final Statement

This project demonstrates a real-world backend system integrated with a trading engine, built with scalable architecture, strong security practices, and clean modular design. It showcases the ability to design, build, and integrate complex systems while maintaining production readiness.
