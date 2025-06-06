import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// User type definitions
export interface User {
  id: number;
  username: string;
  email: string;
  fullName: string;
}

export interface CreateUserDto {
  username: string;
  email: string;
  fullName: string;
}

export interface UpdateUserDto {
  email?: string;
  fullName?: string;
}

// API client functions
export const fetchUsers = async (): Promise<User[]> => {
  const response = await axios.get(`${API_BASE_URL}/users`);
  return response.data;
};

export const fetchUser = async (username: string): Promise<User> => {
  const response = await axios.get(`${API_BASE_URL}/users/${username}`);
  return response.data;
};

export const createUser = async (userData: CreateUserDto): Promise<User> => {
  const response = await axios.post(`${API_BASE_URL}/users`, userData);
  return response.data;
};

export const updateUser = async (username: string, userData: UpdateUserDto): Promise<User> => {
  const response = await axios.patch(`${API_BASE_URL}/users/${username}`, userData);
  return response.data;
};

export const deleteUser = async (userId: number): Promise<{ success: boolean }> => {
  const response = await axios.delete(`${API_BASE_URL}/users/${userId}`);
  return { success: true };
};