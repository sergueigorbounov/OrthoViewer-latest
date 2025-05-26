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
