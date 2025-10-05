import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { makeAuthenticatedRequest } from '../../utils/auth';
import { API_ENDPOINTS } from '../../config/api';
import './FriendRequests.css';

interface FriendRequest {
  sender_id: number;
  nickname: string;
  email: string;
}

const FriendRequests: React.FC = () => {
  const { token } = useAuth();
  const [pendingRequests, setPendingRequests] = useState<FriendRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (token) {
      loadPendingRequests();
    }
  }, [token]);

  const loadPendingRequests = async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.FRIEND_REQUESTS_PENDING);
      if (response.ok) {
        const requests = await response.json();
        setPendingRequests(requests);
      } else {
        setError('Failed to load friend requests');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFriendRequest = async (senderId: number, action: 'accept' | 'reject') => {
    try {
      setError('');
      setSuccess('');

      const response = await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.FRIEND_REQUESTS_HANDLE, {
        method: 'POST',
        body: JSON.stringify({
          sender_id: senderId,
          action: action
        })
      });

      if (response.ok) {
        setSuccess(`Friend request ${action}ed successfully!`);
        // Remove the request from the list
        setPendingRequests(pendingRequests.filter(req => req.sender_id !== senderId));
      } else {
        const errorData = await response.json();
        setError(errorData.error || `Failed to ${action} friend request`);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="friend-requests-container">
        <div className="loading">Loading friend requests...</div>
      </div>
    );
  }

  return (
    <div className="friend-requests-container">
      <div className="friend-requests-header">
        <h2>Friend Requests</h2>
        <p>Manage your incoming friend requests</p>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {success && (
        <div className="success-banner">
          {success}
        </div>
      )}

      {pendingRequests.length === 0 ? (
        <div className="no-requests">
          <div className="no-requests-icon">📭</div>
          <h3>No pending requests</h3>
          <p>You don't have any pending friend requests at the moment.</p>
        </div>
      ) : (
        <div className="requests-list">
          {pendingRequests.map(request => (
            <div key={request.sender_id} className="request-item">
              <div className="request-avatar">
                {request.nickname.charAt(0).toUpperCase()}
              </div>
              <div className="request-info">
                <div className="request-name">{request.nickname}</div>
                <div className="request-email">{request.email}</div>
                <div className="request-status">Wants to be your friend</div>
              </div>
              <div className="request-actions">
                <button
                  onClick={() => handleFriendRequest(request.sender_id, 'accept')}
                  className="accept-btn"
                >
                  ✓ Accept
                </button>
                <button
                  onClick={() => handleFriendRequest(request.sender_id, 'reject')}
                  className="reject-btn"
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FriendRequests;
