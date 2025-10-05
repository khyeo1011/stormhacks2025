import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { makeAuthenticatedRequest } from '../../utils/auth';
import { API_ENDPOINTS } from '../../config/api';
import './AddFriend.css';

interface User {
  id: number;
  email: string;
  nickname: string;
  cumulative_score: number;
}

interface FriendRequest {
  sender_id: number;
  nickname: string;
  email: string;
}

const AddFriend: React.FC = () => {
  const { token } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState<User[]>([]);
  const [pendingRequests, setPendingRequests] = useState<FriendRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState<'search' | 'requests'>('search');

  useEffect(() => {
    if (token) {
      loadPendingRequests();
    }
  }, [token]);

  const loadPendingRequests = async () => {
    try {
      const response = await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.FRIEND_REQUESTS_PENDING);
      if (response.ok) {
        const requests = await response.json();
        setPendingRequests(requests);
      }
    } catch (err) {
      console.error('Failed to load pending requests:', err);
    }
  };

  const searchUsers = async () => {
    if (!searchTerm.trim()) {
      setUsers([]);
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(API_ENDPOINTS.AUTH.USERS);
      if (response.ok) {
        const allUsers = await response.json();
        // Filter users based on search term (nickname or email)
        const filteredUsers = allUsers.filter((user: User) => 
          user.nickname.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.email.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setUsers(filteredUsers);
      } else {
        setError('Failed to search users');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendFriendRequest = async (receiverId: number) => {
    try {
      setError('');
      setSuccess('');
      
      const response = await makeAuthenticatedRequest(API_ENDPOINTS.AUTH.FRIEND_REQUESTS, {
        method: 'POST',
        body: JSON.stringify({
          receiver_id: receiverId
        })
      });

      if (response.ok) {
        setSuccess('Friend request sent successfully!');
        // Remove the user from search results to prevent duplicate requests
        setUsers(users.filter(user => user.id !== receiverId));
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to send friend request');
      }
    } catch (err) {
      setError('Network error. Please try again.');
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

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    searchUsers();
  };

  return (
    <div className="add-friend-container">
      <div className="add-friend-header">
        <h1>Add Friends</h1>
        <p>Search for users and send friend requests to compete together!</p>
      </div>

      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          🔍 Search Users
        </button>
        <button 
          className={`tab-btn ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          📨 Friend Requests ({pendingRequests.length})
        </button>
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

      {activeTab === 'search' && (
        <div className="search-section">
          <form onSubmit={handleSearchSubmit} className="search-form">
            <div className="search-input-group">
              <input
                type="text"
                value={searchTerm}
                onChange={handleSearchChange}
                placeholder="Search by nickname or email..."
                className="search-input"
              />
              <button 
                type="submit" 
                disabled={loading || !searchTerm.trim()}
                className="search-btn"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {users.length > 0 && (
            <div className="users-list">
              <h3>Search Results</h3>
              {users.map(user => (
                <div key={user.id} className="user-item">
                  <div className="user-info">
                    <div className="user-name">{user.nickname}</div>
                    <div className="user-email">{user.email}</div>
                    <div className="user-score">Score: {user.cumulative_score}</div>
                  </div>
                  <button
                    onClick={() => sendFriendRequest(user.id)}
                    className="add-friend-btn"
                  >
                    Add Friend
                  </button>
                </div>
              ))}
            </div>
          )}

          {searchTerm && users.length === 0 && !loading && (
            <div className="no-results">
              <p>No users found matching "{searchTerm}"</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'requests' && (
        <div className="requests-section">
          <h3>Pending Friend Requests</h3>
          {pendingRequests.length === 0 ? (
            <div className="no-requests">
              <p>No pending friend requests</p>
            </div>
          ) : (
            <div className="requests-list">
              {pendingRequests.map(request => (
                <div key={request.sender_id} className="request-item">
                  <div className="request-info">
                    <div className="request-name">{request.nickname}</div>
                    <div className="request-email">{request.email}</div>
                  </div>
                  <div className="request-actions">
                    <button
                      onClick={() => handleFriendRequest(request.sender_id, 'accept')}
                      className="accept-btn"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleFriendRequest(request.sender_id, 'reject')}
                      className="reject-btn"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AddFriend;
