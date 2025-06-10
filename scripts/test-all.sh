#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(dirname "$0")"
TOTAL_TESTS=4
CURRENT_TEST=0

echo_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to run test with progress
run_test() {
    local test_name="$1"
    local test_script="$2"
    CURRENT_TEST=$((CURRENT_TEST + 1))
    
    echo_info "[$CURRENT_TEST/$TOTAL_TESTS] Running $test_name..."
    echo "========================================"
    
    if $SCRIPT_DIR/$test_script; then
        echo_success "$test_name completed successfully!"
    else
        echo_error "$test_name failed!"
        exit 1
    fi
    echo ""
}

echo_info "🧪 Starting comprehensive test suite..."
echo ""

# Run all tests
run_test "Unit Tests" "test-unit.sh"
run_test "Integration Tests" "test-integration.sh" 
run_test "Performance Tests" "test-performance.sh"
run_test "E2E Tests" "test-e2e.sh"

echo_success "🎉 All tests completed successfully!"
echo_info "Test suite finished. Ready for deployment!"