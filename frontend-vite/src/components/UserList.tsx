import { useState, useEffect } from 'react';
import { fetchUsers, deleteUser } from '../api/users';

type User = {
  id: number;
  username: string;
  email: string;
  fullName: string;
};

const UserList = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [userToDelete, setUserToDelete] = useState<number | null>(null);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const fetchedUsers = await fetchUsers();
      setUsers(fetchedUsers);
      setError(null);
    } catch (err) {
      setError(`Error: ${err instanceof Error ? err.message : 'Failed to fetch users'}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleDelete = (userId: number) => {
    setUserToDelete(userId);
    setShowConfirm(true);
  };

  const confirmDelete = async () => {
    if (userToDelete === null) return;
    
    try {
      await deleteUser(userToDelete);
      // Refresh the list
      loadUsers();
      setShowConfirm(false);
      setUserToDelete(null);
    } catch (err) {
      setError(`Error deleting user: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const cancelDelete = () => {
    setShowConfirm(false);
    setUserToDelete(null);
  };

  if (loading) {
    return <div>Loading users...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="user-list">
      <h2>Users</h2>
      
      {users.length === 0 ? (
        <p>No users found</p>
      ) : (
        <ul>
          {users.map(user => (
            <li key={user.id} className="user-item">
              <div>
                <h3>{user.fullName}</h3>
                <p>{user.email}</p>
                <p>Username: {user.username}</p>
              </div>
              <div>
                <button onClick={() => handleDelete(user.id)}>Delete</button>
              </div>
            </li>
          ))}
        </ul>
      )}
      
      {showConfirm && (
        <div className="confirm-dialog">
          <p>Are you sure you want to delete this user?</p>
          <button onClick={confirmDelete}>Confirm</button>
          <button onClick={cancelDelete}>Cancel</button>
        </div>
      )}
    </div>
  );
};

export default UserList;