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
