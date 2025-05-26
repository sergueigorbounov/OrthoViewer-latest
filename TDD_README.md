# BioSemantic Project - TDD Setup

This repository has been set up with a Test-Driven Development (TDD) approach for building a biological data visualization platform. It uses FastAPI for the backend, Vite/React for the frontend, and Docker for containerization.

## Project Structure

```
biosemantic/
├── backend/                   # FastAPI backend code
│   ├── app/                   # Application code
│   │   ├── api/               # API endpoints
│   │   │   └── routes/        # API route modules
│   │   ├── models/            # Pydantic models
│   │   └── main.py            # FastAPI application
│   ├── tests/                 # Tests
│   │   ├── unit/              # Unit tests
│   │   ├── integration/       # Integration tests
│   │   └── performance/       # Performance tests
│   └── Dockerfile             # Backend Docker configuration
├── frontend-vite/             # React frontend code
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   └── Dockerfile             # Frontend Docker configuration
├── nginx/                     # NGINX configuration
├── scripts/                   # Utility scripts
│   ├── backend.sh             # Start backend
│   ├── frontend.sh            # Start frontend
│   ├── docker-backend.sh      # Start backend in Docker
│   ├── docker-frontend.sh     # Start frontend in Docker
│   ├── test-unit.sh           # Run unit tests
│   ├── test-integration.sh    # Run integration tests
│   ├── test-performance.sh    # Run performance tests
│   └── test-e2e.sh            # Run end-to-end tests
├── docker-compose.yml         # Docker Compose configuration
├── end_to_end_tests.py        # End-to-end tests
└── run.sh                     # Main script to run commands
```

## Getting Started

### Development Setup

1. Clone the repository
2. Install dependencies:
   - Backend: Uses conda or venv
   - Frontend: Uses npm

### Running the Application

Use the provided `run.sh` script to execute various commands:

```bash
# Start the backend server
./run.sh backend

# Start the frontend development server
./run.sh frontend

# Start all services with Docker Compose
./run.sh docker-compose
```

### Testing

The project follows Test-Driven Development principles. Tests are structured in different categories:

```bash
# Run backend unit tests
./run.sh test-unit

# Run backend integration tests
./run.sh test-integration

# Run performance tests (ensures < 50ms response time)
./run.sh test-performance

# Run end-to-end tests
./run.sh test-e2e

# Run all tests
./run.sh test-all
```

### Docker

Docker configurations are provided for both frontend and backend:

```bash
# Start backend in Docker
./run.sh docker-backend

# Start frontend in Docker
./run.sh docker-frontend

# Start all services with Docker Compose
./run.sh docker-compose
```

## TDD Workflow

1. Write a failing test
2. Implement the minimal code to make the test pass
3. Refactor while keeping tests green
4. Repeat

## Performance Requirements

- API endpoints must respond in less than 50ms
- Performance tests are included to ensure this requirement is met

## Architecture

- Backend: FastAPI with Pydantic models and SQLAlchemy ORM
- Frontend: React with Vite, TypeScript, and modern tooling
- Infrastructure: Docker, NGINX, CI/CD pipelines

## Contribution Guidelines

1. Create a new branch for your feature
2. Write tests first, then implement the feature
3. Ensure all tests pass
4. Submit a pull request

## License

[License information goes here]