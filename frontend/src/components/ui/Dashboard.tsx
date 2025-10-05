import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { makeAuthenticatedRequest } from '../../utils/auth';
import './Dashboard.css';

interface UserData {
  id: number;
  email: string;
  nickname: string;
  cumulativeScore: number;
  createdAt: string;
}

interface Friend {
  id: number;
  nickname: string;
  email: string;
  cumulative_score: number;
}

interface Trip {
  trip_id: string;
  route_id: string;
  service_id: string;
  trip_headsign: string;
  direction_id: number;
  first_stop: string;
  last_stop: string;
  first_stop_arrival_time: string;
  last_stop_arrival_time: string;
  service_date: string;
  outcome: string | null;
  shape_id: string;
}

interface Prediction {
  id: number;
  trip_id: string;
  predicted_outcome: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { token, logout } = useAuth();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [selectedTrip, setSelectedTrip] = useState<Trip | null>(null);
  const [predictionOutcome, setPredictionOutcome] = useState('');
  const [makingPrediction, setMakingPrediction] = useState(false);
  const predictionSectionRef = useRef<HTMLDivElement | null>(null);
  const [currentTripsPage, setCurrentTripsPage] = useState(1);
  const tripsPerPage = 10;

  useEffect(() => {
    if (token) {
      loadDashboardData();
    }
  }, [token]);


  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [userResponse, tripsResponse, predictionsResponse, friendsResponse] = await Promise.all([
        makeAuthenticatedRequest('http://localhost:8000/auth/profile'),
        fetch('http://localhost:8000/trips'),
        makeAuthenticatedRequest('http://localhost:8000/predictions'),
        makeAuthenticatedRequest('http://localhost:8000/auth/friends')
      ]);

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUserData(userData);
      }

      if (tripsResponse.ok) {
        const tripsData = await tripsResponse.json();
        // Filter trips that haven't started yet
        const availableTrips = tripsData.filter((trip: Trip) => {
          try {
            const now = new Date();
            const tripDateTime = new Date(`${trip.service_date}T${trip.first_stop_arrival_time}`);
            
            // Only show trips that haven't started yet
            return tripDateTime > now;
          } catch (error) {
            console.error('Error parsing trip date/time:', error, trip);
            return false;
          }
        });
        setTrips(availableTrips);
      } else {
        console.error('Failed to load trips:', tripsResponse.status, tripsResponse.statusText);
        setError('Failed to load available trips');
      }

      if (predictionsResponse.ok) {
        const predictionsData = await predictionsResponse.json();
        setPredictions(predictionsData);
        
        // Calculate stats from predictions data
        const totalPredictions = predictionsData.length;
        const today = new Date().toISOString().split('T')[0];
        const todayPredictions = predictionsData.filter((pred: any) => 
          pred.created_at && pred.created_at.startsWith(today)
        ).length;
        
        // Update user data with stats if available
        if (userData) {
          setUserData({
            ...userData,
            cumulativeScore: totalPredictions * 10 // Simple scoring: 10 points per prediction
          });
        }
      }

      if (friendsResponse.ok) {
        const friendsData = await friendsResponse.json();
        setFriends(friendsData);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleMakePrediction = async () => {
    if (!selectedTrip || !predictionOutcome) return;
    
    try {
      setMakingPrediction(true);
      setError(''); // Clear any previous errors
      
      const response = await makeAuthenticatedRequest('http://localhost:8000/predictions', {
        method: 'POST',
        body: JSON.stringify({
          trip_id: selectedTrip.trip_id,
          service_date: selectedTrip.service_date,
          predicted_outcome: predictionOutcome
        })
      });

      if (response.ok) {
        // Just reload predictions instead of all dashboard data
        try {
          const predictionsResponse = await makeAuthenticatedRequest('http://localhost:8000/predictions');
          if (predictionsResponse.ok) {
            const predictionsData = await predictionsResponse.json();
            setPredictions(predictionsData);
          }
        } catch (err) {
          const message = err instanceof Error
            ? err.message
            : typeof err === 'string'
            ? err
            : 'Failed to reload predictions';
          setError(message);
          setTimeout(() => setError(''), 5000);
        }
        
        setSelectedTrip(null);
        setPredictionOutcome('');
        setSuccessMessage('Prediction submitted successfully!');
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        let errorMessage = 'Failed to make prediction';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.msg || `Server error (${response.status})`;
        } catch (parseError) {
          errorMessage = `Server error (${response.status})`;
        }
        
        setError(errorMessage);
        // Clear error message after 5 seconds
        setTimeout(() => setError(''), 5000);
      }
    } catch (err) {
      setError('Network error. Please try again.');
      // Clear error message after 5 seconds
      setTimeout(() => setError(''), 5000);
    } finally {
      setMakingPrediction(false);
    }
  };

  const handleTripClick = (trip: Trip) => {
    setSelectedTrip(trip);
    setPredictionOutcome('');
    if (predictionSectionRef.current) {
      predictionSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const totalTripsPages = Math.max(1, Math.ceil(trips.length / tripsPerPage));
  const startIndex = (currentTripsPage - 1) * tripsPerPage;
  const endIndex = startIndex + tripsPerPage;
  const paginatedTrips = trips.slice(startIndex, endIndex);
  const goToPrevTripsPage = () => setCurrentTripsPage(prev => Math.max(1, prev - 1));
  const goToNextTripsPage = () => setCurrentTripsPage(prev => Math.min(totalTripsPages, prev + 1));

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading your dashboard...</div>
      </div>
    );
  }

  if (error && !userData) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  const todayPredictions = predictions.filter(p => {
    const predictionDate = new Date(p.created_at);
    const today = new Date();
    return predictionDate.toDateString() === today.toDateString();
  });

  const accuracy = predictions.length > 0 ? 
    Math.round((predictions.filter(p => p.predicted_outcome === 'on_time').length / predictions.length) * 100) : 0;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1 className="dashboard-title">Welcome back, {userData?.nickname}!</h1>
          <p className="dashboard-subtitle">Make predictions and climb the leaderboard</p>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="success-banner">
          {successMessage}
        </div>
      )}


      <div className="dashboard-grid">
        {/* Stats Cards */}
        <div className="stats-section">
          <div className="stat-card primary">
            <div className="stat-icon">🎯</div>
            <div className="stat-content">
              <div className="stat-value">{userData?.cumulativeScore || 0}</div>
              <div className="stat-label">Total Score</div>
            </div>
          </div>
          <div className="stat-card secondary">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <div className="stat-value">{todayPredictions.length}</div>
              <div className="stat-label">Today's Predictions</div>
            </div>
          </div>
          <div className="stat-card success">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-value">{accuracy}%</div>
              <div className="stat-label">Accuracy</div>
            </div>
          </div>
          <div className="stat-card warning">
            <div className="stat-icon">🚌</div>
            <div className="stat-content">
              <div className="stat-value">{trips.length}</div>
              <div className="stat-label">Available Trips</div>
            </div>
          </div>
        </div>

        {/* Friends Scores Section */}
        <div className="friends-section">
          <div className="friends-header">
            <h2>Friends Scores</h2>
            <div className="friends-actions">
              <button 
                onClick={() => window.location.href = '/add-friend'}
                className="add-friend-btn"
              >
                + Add Friend
              </button>
              <button 
                onClick={() => window.location.href = '/friend-requests'}
                className="view-requests-btn"
              >
                📨 Requests
              </button>
            </div>
          </div>
          {friends.length === 0 ? (
            <div className="no-friends">
              <div className="no-friends-icon">👥</div>
              <h3>No friends yet</h3>
              <p>Add friends to see their scores and compete together!</p>
              <button 
                onClick={() => window.location.href = '/add-friend'}
                className="cta-add-friend-btn"
              >
                Find Friends
              </button>
            </div>
          ) : (
            <div className="friends-list">
              {friends
                .sort((a, b) => b.cumulative_score - a.cumulative_score)
                .map((friend, index) => (
                  <div key={friend.id} className="friend-item">
                    <div className="friend-rank">#{index + 1}</div>
                    <div className="friend-info">
                      <div className="friend-name">{friend.nickname}</div>
                      <div className="friend-email">{friend.email}</div>
                    </div>
                    <div className="friend-score">{friend.cumulative_score}</div>
                  </div>
                ))}
            </div>
          )}
        </div>

        {/* Make Prediction Section */}
        <div className="prediction-section" ref={predictionSectionRef}>
          <h2>Make a Prediction</h2>
          <div className="prediction-form">
            <div className="form-group">
              <label>Select Trip</label>
              <select 
                value={selectedTrip?.trip_id || ''} 
                onChange={(e) => {
                  const trip = trips.find(t => t.trip_id === e.target.value);
                  setSelectedTrip(trip || null);
                }}
                className="trip-select"
              >
                <option value="">Choose a trip...</option>
                {trips.map(trip => (
                  <option key={trip.trip_id} value={trip.trip_id}>
                    {trip.trip_headsign}: {trip.first_stop} → {trip.last_stop} ({trip.first_stop_arrival_time})
                  </option>
                ))}
              </select>
            </div>

            {selectedTrip && (
              <div className="form-group">
                <label>Prediction</label>
                <div className="prediction-options">
                  <button
                    type="button"
                    className={`prediction-btn ${predictionOutcome === 'on_time' ? 'active' : ''}`}
                    onClick={() => setPredictionOutcome('on_time')}
                  >
                    ✅ On Time
                  </button>
                  <button
                    type="button"
                    className={`prediction-btn ${predictionOutcome === 'late' ? 'active' : ''}`}
                    onClick={() => setPredictionOutcome('late')}
                  >
                    ⏰ Late
                  </button>
                </div>
              </div>
            )}

            {selectedTrip && predictionOutcome && (
              <button
                onClick={handleMakePrediction}
                disabled={makingPrediction}
                className="submit-prediction-btn"
              >
                {makingPrediction ? 'Making Prediction...' : 'Submit Prediction'}
              </button>
            )}

            {error && (
              <div className="form-error">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Recent Predictions */}
        <div className="recent-predictions">
          <h2>Recent Predictions</h2>
          {predictions.length === 0 ? (
            <div className="no-predictions">
              <p>No predictions yet. Make your first prediction above!</p>
            </div>
          ) : (
            <div className="predictions-list">
              {predictions.slice(0, 5).map(prediction => (
                <div key={prediction.id} className="prediction-item">
                  <div className="prediction-trip">
                    Trip {prediction.trip_id}
                  </div>
                  <div className={`prediction-outcome ${prediction.predicted_outcome}`}>
                    {prediction.predicted_outcome === 'on_time' && '✅ On Time'}
                    {prediction.predicted_outcome === 'late' && '⏰ Late'}
                  </div>
                  <div className="prediction-date">
                    {new Date(prediction.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Available Trips */}
        <div className="available-trips">
          <h2>Available Trips</h2>
          <div className="trips-list">
            {paginatedTrips.map(trip => (
              <div
                key={trip.trip_id}
                className={`trip-item ${selectedTrip?.trip_id === trip.trip_id ? 'selected' : ''}`}
                onClick={() => handleTripClick(trip)}
                role="button"
                aria-label={`Select trip from ${trip.first_stop} to ${trip.last_stop} at ${trip.first_stop_arrival_time}`}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleTripClick(trip);
                  }
                }}
              >
                <div className="trip-route">
                  {trip.first_stop} → {trip.last_stop}
                </div>
                <div className="trip-time">
                  {trip.first_stop_arrival_time}
                </div>
                <div className="trip-status">
                  {predictions.some(p => p.trip_id === trip.trip_id) ? '✅ Predicted' : '⏳ Available'}
                </div>
              </div>
            ))}
          </div>
          <div className="trips-pagination">
            <button
              className="page-btn"
              onClick={goToPrevTripsPage}
              disabled={currentTripsPage === 1}
            >
              ← Prev
            </button>
            <div className="page-info">
              Page {currentTripsPage} of {totalTripsPages}
            </div>
            <button
              className="page-btn"
              onClick={goToNextTripsPage}
              disabled={currentTripsPage === totalTripsPages}
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
