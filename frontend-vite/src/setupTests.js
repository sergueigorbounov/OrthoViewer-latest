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
