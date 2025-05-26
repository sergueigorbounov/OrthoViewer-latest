#!/bin/bash

# TDD Environment Setup for BioSemanticViz
# This script sets up the complete TDD environment with test templates and utilities

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=== BioSemanticViz TDD Environment Setup ===${NC}"

# Create test directories
echo -e "${CYAN}Creating test directory structure...${NC}"

# Frontend test directories
mkdir -p frontend/src/__tests__/{components,utils,services,integration}
mkdir -p frontend/src/__tests__/templates
mkdir -p frontend/src/__tests__/mocks

# Backend test directories  
mkdir -p backend/tests/{unit,integration,performance}
mkdir -p backend/tests/fixtures

# Create test configuration files
echo -e "${CYAN}Setting up test configuration...${NC}"

# Frontend: Jest configuration enhancement
cat > frontend/src/setupTests.js << 'EOF'
// Enhanced test setup for BioSemanticViz
import '@testing-library/jest-dom';

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock D3 for testing
jest.mock('d3', () => ({
  select: jest.fn(() => ({
    selectAll: jest.fn(() => ({
      data: jest.fn(() => ({
        enter: jest.fn(() => ({
          append: jest.fn(() => ({
            attr: jest.fn(),
            style: jest.fn(),
            text: jest.fn(),
            on: jest.fn()
          }))
        }))
      }))
    })),
    append: jest.fn(() => ({
      attr: jest.fn(),
      style: jest.fn()
    })),
    attr: jest.fn(),
    style: jest.fn()
  })),
  hierarchy: jest.fn(),
  tree: jest.fn(() => ({
    size: jest.fn()
  })),
  zoom: jest.fn(() => ({
    scaleExtent: jest.fn(() => ({
      on: jest.fn()
    }))
  }))
}));

// Suppress console.error and console.warn in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('deprecated') || args[0].includes('Warning'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});
EOF

# Frontend: Enhanced package.json test scripts
echo -e "${CYAN}Updating frontend package.json test scripts...${NC}"

# Create a backup of package.json
cp frontend/package.json frontend/package.json.bak

# Add test scripts using node
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('frontend/package.json', 'utf8'));

pkg.scripts = {
  ...pkg.scripts,
  'test': 'react-scripts test',
  'test:coverage': 'react-scripts test --coverage --watchAll=false',
  'test:ci': 'react-scripts test --coverage --watchAll=false --ci',
  'test:debug': 'react-scripts --inspect-brk test --runInBand --no-cache',
  'test:integration': 'react-scripts test --testPathPattern=integration',
  'test:unit': 'react-scripts test --testPathPattern=unit',
  'lint': 'eslint src/ --ext .js,.jsx,.ts,.tsx',
  'lint:fix': 'eslint src/ --ext .js,.jsx,.ts,.tsx --fix',
  'type-check': 'tsc --noEmit'
};

// Add jest configuration
pkg.jest = {
  ...pkg.jest,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  testPathIgnorePatterns: [
    '/node_modules/',
    '/build/'
  ]
};

fs.writeFileSync('frontend/package.json', JSON.stringify(pkg, null, 2));
"

# Backend: pytest configuration
cat > backend/pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=70

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
EOF

# Backend: conftest.py for shared fixtures
cat > backend/tests/conftest.py << 'EOF'
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import your app
from app.fastapi_main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'ORTHOFINDER_DATA_DIR': '/tmp/test_data',
        'CORS_ORIGINS': 'http://localhost:3000'
    }):
        yield

@pytest.fixture(scope="session")
def mock_biological_data():
    """Session-scoped biological test data"""
    return {
        "test_newick": "((At:0.1,Os:0.2):0.05,Zm:0.15);",
        "test_orthogroups": {
            'Orthogroup': ['OG0000001', 'OG0000002'],
            'At': ['AT1G01010,AT1G01020', 'AT2G01010'],
            'Os': ['OS01G0100100', 'OS02G0100100'],
            'Zm': ['ZM01G00010', '']
        },
        "test_species_mapping": {
            'At': 'Arabidopsis thaliana',
            'Os': 'Oryza sativa',
            'Zm': 'Zea mays'
        }
    }
EOF

# Create test data fixtures
echo -e "${CYAN}Creating test data fixtures...${NC}"

# Frontend test utilities
cat > frontend/src/__tests__/utils/testUtils.js << 'EOF'
import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme();

export const renderWithProviders = (ui, options = {}) => {
  const Wrapper = ({ children }) => (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        {children}
      </ThemeProvider>
    </BrowserRouter>
  );

  return render(ui, { wrapper: Wrapper, ...options });
};

export const createMockApiResponse = (data, success = true) => ({
  ok: success,
  json: async () => ({ success, ...data }),
});

export const setupFetchMock = (responses = {}) => {
  global.fetch = jest.fn((url) => {
    const response = responses[url] || responses.default;
    return Promise.resolve(response || createMockApiResponse({}));
  });
};

export const mockD3Selection = () => ({
  select: jest.fn(() => mockD3Selection()),
  selectAll: jest.fn(() => mockD3Selection()),
  data: jest.fn(() => mockD3Selection()),
  enter: jest.fn(() => mockD3Selection()),
  append: jest.fn(() => mockD3Selection()),
  attr: jest.fn(() => mockD3Selection()),
  style: jest.fn(() => mockD3Selection()),
  text: jest.fn(() => mockD3Selection()),
  on: jest.fn(() => mockD3Selection()),
  transition: jest.fn(() => mockD3Selection()),
  duration: jest.fn(() => mockD3Selection()),
  call: jest.fn(() => mockD3Selection())
});
EOF

# Create example test files
echo -e "${CYAN}Creating example test files...${NC}"

# Frontend component test example
cat > frontend/src/__tests__/components/Header.test.js << 'EOF'
import React from 'react';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../utils/testUtils';
import Header from '../../components/Header';

describe('Header Component', () => {
  test('renders application title', () => {
    renderWithProviders(<Header />);
    expect(screen.getByText(/BioSemanticViz/i)).toBeInTheDocument();
  });

  test('renders navigation links', () => {
    renderWithProviders(<Header />);
    expect(screen.getByText(/Home/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload/i)).toBeInTheDocument();
    expect(screen.getByText(/Explorer/i)).toBeInTheDocument();
  });
});
EOF

# Backend API test example
cat > backend/tests/unit/test_api_endpoints.py << 'EOF'
import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client):
    """Test the root endpoint returns basic info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "BioSemanticViz" in data["message"]

def test_status_endpoint(client):
    """Test the status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200

def test_api_status_endpoint(client):
    """Test the API status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
EOF

# Create TDD workflow helpers
cat > tdd-helpers.sh << 'EOF'
#!/bin/bash

# TDD Helper Functions for BioSemanticViz

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Run specific test with watch
tdd-test() {
    if [ -z "$1" ]; then
        echo "Usage: tdd-test <test-name>"
        echo "Example: tdd-test 'OrthologueSearch'"
        return 1
    fi
    
    echo -e "${BLUE}Running TDD for: $1${NC}"
    ./tdd.sh --test="$1" --coverage
}

# Run frontend tests only
tdd-frontend() {
    echo -e "${BLUE}TDD Frontend Only${NC}"
    ./tdd.sh --no-backend --test="$1"
}

# Run backend tests only  
tdd-backend() {
    echo -e "${BLUE}TDD Backend Only${NC}"
    cd backend
    if [ -n "$1" ]; then
        pytest -xvs -k "$1" --cov=app
    else
        pytest -xvs --cov=app
    fi
    cd ..
}

# Run integration tests
tdd-integration() {
    echo -e "${BLUE}Running Integration Tests${NC}"
    ./tdd.sh --coverage
    sleep 5
    cd backend && pytest -m integration && cd ..
}

# Create new test file from template
tdd-new-test() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: tdd-new-test <component-name> <frontend|backend>"
        echo "Example: tdd-new-test PhylogeneticTree frontend"
        return 1
    fi
    
    COMPONENT=$1
    TYPE=$2
    
    if [ "$TYPE" = "frontend" ]; then
        TEST_FILE="frontend/src/__tests__/components/${COMPONENT}.test.js"
        cat > "$TEST_FILE" << EOF
import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../utils/testUtils';
import $COMPONENT from '../../components/$COMPONENT';

describe('$COMPONENT Component', () => {
  test('renders without crashing', () => {
    renderWithProviders(<$COMPONENT />);
    // Add your test assertions here
  });

  // Add more tests following TDD Red-Green-Refactor cycle
});
EOF
        echo -e "${GREEN}Created frontend test: $TEST_FILE${NC}"
        
    elif [ "$TYPE" = "backend" ]; then
        TEST_FILE="backend/tests/unit/test_${COMPONENT,,}.py"
        cat > "$TEST_FILE" << EOF
import pytest
from fastapi.testclient import TestClient

class Test$COMPONENT:
    """TDD Tests for $COMPONENT"""
    
    def test_placeholder(self, client):
        """Placeholder test - replace with actual test"""
        # RED: Write a failing test first
        assert True  # Replace with actual test
    
    # Add more tests following TDD Red-Green-Refactor cycle
EOF
        echo -e "${GREEN}Created backend test: $TEST_FILE${NC}"
    else
        echo "Invalid type. Use 'frontend' or 'backend'"
        return 1
    fi
}

# Show test coverage report
tdd-coverage() {
    echo -e "${BLUE}Generating Coverage Reports${NC}"
    
    # Frontend coverage
    echo -e "${YELLOW}Frontend Coverage:${NC}"
    cd frontend && npm run test:coverage && cd ..
    
    # Backend coverage  
    echo -e "${YELLOW}Backend Coverage:${NC}"
    cd backend && pytest --cov=app --cov-report=html && cd ..
    
    echo -e "${GREEN}Coverage reports generated!${NC}"
    echo "Frontend: frontend/coverage/lcov-report/index.html"
    echo "Backend: backend/htmlcov/index.html"
}

# Lint all code
tdd-lint() {
    echo -e "${BLUE}Running Linters${NC}"
    
    # Frontend linting
    echo -e "${YELLOW}Frontend Linting:${NC}"
    cd frontend && npm run lint && cd ..
    
    # Backend linting
    echo -e "${YELLOW}Backend Linting:${NC}"
    cd backend && black --check app/ && flake8 app/ && cd ..
}

echo -e "${GREEN}TDD Helper functions loaded!${NC}"
echo "Available commands:"
echo "  tdd-test <name>     - Run specific test with coverage"
echo "  tdd-frontend        - Frontend tests only"
echo "  tdd-backend         - Backend tests only"
echo "  tdd-integration     - Run integration tests"
echo "  tdd-new-test        - Create new test file"
echo "  tdd-coverage        - Generate coverage reports"
echo "  tdd-lint           - Run linters"
EOF

chmod +x tdd-helpers.sh

# Update the main TDD script to be executable
chmod +x tdd.sh

echo -e "${GREEN}✅ TDD Environment Setup Complete!${NC}"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "1. Source the helper functions: ${YELLOW}source tdd-helpers.sh${NC}"
echo "2. Start TDD development: ${YELLOW}./tdd.sh${NC}"
echo "3. Create new tests: ${YELLOW}tdd-new-test ComponentName frontend${NC}"
echo "4. Run specific tests: ${YELLOW}tdd-test 'OrthologueSearch'${NC}"
echo ""
echo -e "${BLUE}Happy Test-Driven Development! 🧬✨${NC}"