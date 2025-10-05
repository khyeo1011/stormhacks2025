// Utility function to make authenticated API calls
export const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers,
  });
};

// Helper function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

// Helper function to get token
export const getToken = (): string | null => {
  return localStorage.getItem('token');
};
