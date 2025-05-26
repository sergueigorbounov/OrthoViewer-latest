#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"

# Run unit tests
echo "=== Running Unit Tests ==="
$SCRIPT_DIR/test-unit.sh

# Run integration tests
echo "=== Running Integration Tests ==="
$SCRIPT_DIR/test-integration.sh

# Run performance tests
echo "=== Running Performance Tests ==="
$SCRIPT_DIR/test-performance.sh

# Run E2E tests
echo "=== Running E2E Tests ==="
$SCRIPT_DIR/test-e2e.sh

echo "=== All tests completed successfully! ==="