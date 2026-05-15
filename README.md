# Scalable Backend System with Integrated Trading Engine

## 1. Project Overview

This project is a production-ready, scalable backend system integrated with a cryptocurrency trading engine. It demonstrates industry-standard architectural patterns, secure authentication mechanisms, and resilient external API integrations. Designed to operate identically via a RESTful API and a Command Line Interface (CLI), the system allows users to securely authenticate, manage tasks, and execute live cryptocurrency trades via the Binance Futures Testnet.

## 2. Features

**Authentication & Authorization**
* Secure JWT-based authentication
* Role-Based Access Control (RBAC) distinguishing between standard users and administrators
* Automatic token expiry validation and secure password hashing

**Task Management**
* Complete CRUD (Create, Read, Update, Delete) functionality for task management
* Strict data isolation ensuring users can only access their respective data

**Trading System**
* Live integration with the Binance Futures Testnet
* Support for MARKET and LIMIT order executions
* Centralized trading engine shared seamlessly between the API and the CLI bot

**System Reliability & Operations**
* Automated database schema migrations
* Structured JSON logging with request lifecycle tracking
* Comprehensive automated testing suite
* Dockerized environments for reliable deployments

## 3. Architecture

The backend implements a Clean Architecture pattern, strictly separating concerns to ensure maintainability and testability. The application is logically grouped into layers:

* **Routes**: Handle HTTP request mapping and dispatching.
* **Controllers**: Process input validation and format output responses.
* **Services**: Contain all core business logic and orchestrate domain workflows.
* **Models**: Define the database schema and data structures.
* **Trading Module**: A decoupled, shared library utilized by both the web controllers and the CLI tool, preventing logic duplication.

## 4. Tech Stack

**Backend**
* Python 3.x
* Flask
* SQLAlchemy (ORM)
* Flask-JWT-Extended
* bcrypt
* Flask-Migrate
* Flask-Limiter

**Frontend**
* Next.js (React)

**CLI**
* argparse

**Database**
* PostgreSQL

**External Integration**
* python-binance

**Tooling & DevOps**
* Pytest (Testing)
* Swagger / Postman (Documentation)
* Docker & Docker Compose
* python-dotenv

## 5. Project Structure

```text
.
├── backend/
│   ├── controllers/      # Request parsing and response formatting
│   ├── models/           # SQLAlchemy database models
│   ├── routes/           # Blueprint definitions and URL routing
│   ├── schemas/          # Input/output validation schemas
│   ├── services/         # Core business logic and data manipulation
│   ├── trading/          # Reusable Binance trading engine
│   └── utils/            # Shared utilities (logging, error handling)
├── cli/                  # Command Line Interface application
├── frontend/             # Next.js web application
├── logs/                 # Structured application logs
├── tests/                # Automated pytest suite
└── migrations/           # Database migration scripts
```

## 6. Setup Instructions

### Prerequisites
* Python 3.10 or higher
* Node.js 18 or higher
* PostgreSQL database server
* Binance Testnet Account (API Key and Secret)

### Backend Setup

1. Clone the repository and navigate to the project root.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the environment variables by creating a `.env` file (see Environment Variables section).
5. Initialize the database and run migrations:
   ```bash
   flask db upgrade
   ```
6. Start the Flask application:
   ```bash
   flask run --port=5000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

### CLI Usage

The CLI tool utilizes the same core trading module as the backend. It must be run within the active Python virtual environment.

```bash
# Execute a MARKET order
python cli/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Execute a LIMIT order
python cli/cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 3000.50
```

*Arguments:*
* `--symbol`: The trading pair (e.g., BTCUSDT)
* `--side`: The order side (BUY or SELL)
* `--type`: The order type (MARKET or LIMIT)
* `--quantity`: The amount to trade
* `--price`: The limit price (Required only for LIMIT orders)

### Running Tests

The application includes an automated test suite leveraging `pytest`.

```bash
# Ensure your virtual environment is active
source .venv/bin/activate

# Execute the test suite
pytest -v
```

## 7. Environment Variables

Create a `.env` file in the root directory containing the following required configurations:

* `FLASK_ENV`: Deployment environment (development, testing, production).
* `SECRET_KEY`: Cryptographic key for Flask sessions.
* `JWT_SECRET_KEY`: Cryptographic key for signing JSON Web Tokens.
* `DATABASE_URL`: Connection string for PostgreSQL.
* `BINANCE_API_KEY`: API Key for the Binance Futures Testnet.
* `BINANCE_API_SECRET`: API Secret for the Binance Futures Testnet.
* `BINANCE_TESTNET`: Boolean flag to ensure staging environments do not execute real trades.
* `LOG_LEVEL`: Configurable application verbosity (INFO, DEBUG, ERROR).
* `LOG_FILE`: Filepath destination for structured logs.

## 8. API Overview

The REST API strictly adheres to standard HTTP methods and normalized JSON responses. The base URL for all endpoints is `http://localhost:5000/api/v1`.

**Key Endpoints:**
* `POST /auth/register` - Register a new user
* `POST /auth/login` - Authenticate and retrieve a JWT
* `GET /tasks` - Retrieve tasks for the authenticated user
* `POST /tasks` - Create a new task
* `POST /trades/order` - Execute a new trade
* `GET /trades/history` - Retrieve trade execution history

Detailed endpoint contracts are documented in the provided `swagger.yaml` and can be imported directly into Postman or Swagger UI.

## 9. Example Usage

### Example API Request (Create Trade)

**Request:**
```http
POST /api/v1/trades/order
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": 0.01
}
```

**Response:**
```json
{
  "message": "Trade executed",
  "data": {
    "order_id": "123456789",
    "status": "FILLED",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET"
  }
}
```

## 10. Logging

The application utilizes a structured JSON logging system to ensure production observability and traceability.

Logs capture critical context including:
* Generated `request_id` for tracing a request across the entire application lifecycle.
* `execution_time_ms` for performance monitoring.
* Evaluated `user_id` to correlate backend actions with specific authenticated clients.
* Target `endpoint` and HTTP `method`.

This structured format guarantees that external failures, such as network timeouts to the Binance API, can be diagnosed and isolated entirely via log aggregators.

## 11. Security

The system is fortified with multiple layers of security designed for production environments:
* **Authentication**: Enforced via `Flask-JWT-Extended` with strictly managed token expiration.
* **Password Hashing**: Cryptographically secure hashing utilizing `bcrypt`.
* **Rate Limiting**: Implementation of `Flask-Limiter` to mitigate brute-force attacks against authentication endpoints.
* **Input Validation**: Hardened marshmallow schemas applied at the controller level to sanitize and validate all incoming payload definitions.

## 12. Testing

The backend relies on `pytest` to enforce regression prevention.
The test suite isolates testing data using a dedicated in-memory or localized test database, effectively covering:
* Authentication rules and conflict state handling (e.g., duplicate emails).
* Task ownership enforcement ensuring users cannot arbitrarily view foreign records.
* Trading logic boundaries, leveraging `pytest-mock` to simulate Binance API network responses and enforce parameter validations without executing live network requests.

## 13. Deployment

The system is structured for containerized deployment.
* Application environments are decoupled from the codebase using `.env` injections.
* The repository can be orchestrated using Docker and Docker Compose, leveraging multi-stage builds to optimize the container footprint for production clusters.

## 14. Future Improvements

To scale this application further, the following infrastructural enhancements are recommended:
* **Redis Integration**: To transition rate limiting and session caching from localized memory to a distributed store.
* **Background Jobs**: Implementing Celery to handle trading executions and webhooks asynchronously.
* **Microservices Strategy**: Decoupling the Trading Engine from the User/Task API to scale high-frequency trade components independently.

## 15. Conclusion

This project serves as a robust blueprint for engineering highly scalable, maintainable, and secure backend architectures. By strictly enforcing separation of concerns, defensive security measures, and extensive observability, the system stands as a reliable, production-ready foundation capable of continuous integration and scaling.
