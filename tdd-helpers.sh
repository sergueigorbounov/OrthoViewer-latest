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
