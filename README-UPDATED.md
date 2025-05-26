# Application Project

A modern application with separate backend and frontend components following Test-Driven Development practices.

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/              # Application code
│   ├── tests/            # Backend tests
│   ├── Dockerfile        # Backend Docker configuration
│   └── tdd.sh            # Backend TDD script
│
├── frontend-vite/        # Vite/React frontend
│   ├── src/              # Frontend source code
│   ├── tests/            # Frontend tests
│   ├── Dockerfile        # Frontend Docker configuration
│   └── tdd.sh            # Frontend TDD script
│
├── docker-compose.yml    # Production Docker Compose
├── docker-compose.dev.yml # Development Docker Compose
└── run-app.sh            # Main application runner
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose (optional)

### Running the Application

You can run the application using the provided script:

```bash
# Make the script executable
chmod +x run-app.sh

# Start both backend and frontend
./run-app.sh

# Start only backend
./run-app.sh backend

# Start only frontend
./run-app.sh frontend
```

### Test-Driven Development

This project follows Test-Driven Development (TDD) principles. You can run tests with:

```bash
# Run all tests
./run-app.sh test

# Run backend tests only
cd backend
./tdd.sh test

# Run frontend tests only
cd frontend-vite
./tdd.sh test
```

For TDD workflow:

1. Write a failing test
2. Write code to make the test pass
3. Refactor while keeping tests green
4. Repeat

### Docker Deployment

To run the application with Docker:

```bash
# Production mode
./run-app.sh docker

# Development mode (with hot reloading)
./run-app.sh docker-dev
```

## Development Workflow

1. Run tests in watch mode while developing:
   ```
   cd backend
   ./tdd.sh test
   ```

2. Implement your changes following TDD:
   - Write a failing test
   - Implement the feature
   - Make sure the test passes
   - Refactor if needed

3. Run linting before committing:
   ```
   cd backend
   ./tdd.sh lint
   ```

## API Documentation

When the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc