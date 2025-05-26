import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import UserList from './UserList';
import { fetchUsers, deleteUser } from '../api/users';

// Mock the API calls
vi.mock('../api/users', () => ({
  fetchUsers: vi.fn(),
  deleteUser: vi.fn()
}));

const mockUsers = [
  { id: 1, username: 'user1', email: 'user1@example.com', fullName: 'User One' },
  { id: 2, username: 'user2', email: 'user2@example.com', fullName: 'User Two' }
];

describe('UserList Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default mock implementation
    (fetchUsers as any).mockResolvedValue(mockUsers);
    (deleteUser as any).mockResolvedValue({ success: true });
  });

  test('displays a list of users', async () => {
    render(<UserList />);
    
    // Check loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('User One')).toBeInTheDocument();
    });
    
    // Verify all users are displayed
    expect(screen.getByText('User One')).toBeInTheDocument();
    expect(screen.getByText('User Two')).toBeInTheDocument();
    expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    expect(screen.getByText('user2@example.com')).toBeInTheDocument();
  });

  test('shows error message when API call fails', async () => {
    // Mock API failure
    (fetchUsers as any).mockRejectedValue(new Error('Failed to fetch users'));
    
    render(<UserList />);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/failed to fetch users/i)).toBeInTheDocument();
  });

  test('deletes a user when delete button is clicked', async () => {
    render(<UserList />);
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('User One')).toBeInTheDocument();
    });
    
    // Find delete buttons
    const deleteButtons = screen.getAllByText(/delete/i);
    
    // Click the first delete button
    userEvent.click(deleteButtons[0]);
    
    // Confirm deletion
    userEvent.click(screen.getByText(/confirm/i));
    
    // Verify deleteUser was called
    expect(deleteUser).toHaveBeenCalledWith(1);
    
    // Verify fetchUsers was called again to refresh the list
    expect(fetchUsers).toHaveBeenCalledTimes(2);
  });
});