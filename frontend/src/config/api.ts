// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    REGISTER: `${API_BASE_URL}/auth/register`,
    PROFILE: `${API_BASE_URL}/auth/profile`,
    FRIENDS: `${API_BASE_URL}/auth/friends`,
    USERS: `${API_BASE_URL}/auth/users`,
    FRIEND_REQUESTS: `${API_BASE_URL}/auth/friend-requests`,
    FRIEND_REQUESTS_PENDING: `${API_BASE_URL}/auth/friend-requests/pending`,
    FRIEND_REQUESTS_HANDLE: `${API_BASE_URL}/auth/friend-requests/handle`,
  },
  TRIPS: `${API_BASE_URL}/trips`,
  PREDICTIONS: `${API_BASE_URL}/predictions`,
  LEADERBOARD: `${API_BASE_URL}/leaderboard`,
} as const;

export default API_BASE_URL;
