// Utility function to make authenticated API calls
export const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const doFetch = async (): Promise<Response> => {
    return fetch(url, {
      ...options,
      headers,
    });
  };

  let response = await doFetch();

  // If unauthorized, try to refresh the access token once
  if (response.status === 401) {
    const refreshed = await attemptRefreshToken();
    if (refreshed) {
      const newToken = localStorage.getItem('token');
      if (newToken) headers['Authorization'] = `Bearer ${newToken}`;
      response = await doFetch();
    }
  }

  return response;
};


// Helper function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

// Helper function to get token
export const getToken = (): string | null => {
  return localStorage.getItem('token');
};
