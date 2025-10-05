import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_ENDPOINTS } from '../../config/api';
import './Account.css';

interface UserData {
  id: number;
  email: string;
  nickname: string;
  cumulativeScore: number;
  createdAt: string;
}

const Account: React.FC = () => {
  const { token, logout } = useAuth();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchUserData();
    }
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.AUTH.PROFILE, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(data);
      } else {
        setError('Failed to load profile data');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="account-container">
        <div className="loading">Loading your profile...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="account-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!userData) {
    return (
      <div className="account-container">
        <div className="error-message">No user data available</div>
      </div>
    );
  }

  // Calculate daily score (placeholder - you might want to implement this based on your scoring logic)
  const dailyScore = 0; // This would be calculated based on today's predictions

  return (
    <div className="account-container">
      <div className="account-header">
        <h1 className="account-title">My Account</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      <div className="account-content">
        <div className="profile-section">
          <h2>Profile Information</h2>
          <div className="profile-info">
            <div className="info-item">
              <label>Nickname:</label>
              <span>{userData.nickname}</span>
            </div>
            <div className="info-item">
              <label>Email:</label>
              <span>{userData.email}</span>
            </div>
            <div className="info-item">
              <label>Member since:</label>
              <span>{new Date(userData.createdAt).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="scores-section">
          <h2>Your Scores</h2>
          <div className="score-cards">
            <div className="score-card">
              <div className="score-label">Daily Score</div>
              <div className="score-value">{dailyScore}</div>
              <div className="score-description">Points earned today</div>
            </div>
            <div className="score-card">
              <div className="score-label">Total Score</div>
              <div className="score-value">{userData.cumulativeScore}</div>
              <div className="score-description">All-time points</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;
