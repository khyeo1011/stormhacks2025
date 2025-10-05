import React, { useEffect, useState } from 'react';
import { makeAuthenticatedRequest } from '../../utils/auth';
import { API_ENDPOINTS } from '../../config/api';
import './Leaderboard.css';

interface LeaderboardEntry {
  nickname: string;
  cumulative_score: number;
}

const Leaderboard: React.FC = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLeaderboard = async () => {
      try {
        setLoading(true);
        setError(null);
        // /leaderboard does not require auth on backend, but use helper for consistency
        const response = await makeAuthenticatedRequest(API_ENDPOINTS.LEADERBOARD);
        if (!response.ok) {
          throw new Error(`Failed to load leaderboard (${response.status})`);
        }
        const data = await response.json();
        setEntries(Array.isArray(data) ? data : []);
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Failed to load leaderboard';
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    loadLeaderboard();
  }, []);

  return (
    <div className="leaderboard-container">
      <h1 className="leaderboard-title">Leaderboard</h1>
      <p className="leaderboard-subtitle">Top players by cumulative score</p>

      {error && !loading && <div className="leaderboard-error">{error}</div>}

      <div className="leaderboard-table" role="table" aria-label="Leaderboard">
        <div className="leaderboard-header" role="row">
          <div className="leaderboard-col rank" role="columnheader">#</div>
          <div className="leaderboard-col name" role="columnheader">Nickname</div>
          <div className="leaderboard-col score" role="columnheader">Score</div>
        </div>

        {loading ? (
          <div className="leaderboard-placeholder">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="leaderboard-row" role="row" aria-hidden="true">
                <div className="leaderboard-col rank skeleton" />
                <div className="leaderboard-col name skeleton" />
                <div className="leaderboard-col score skeleton" />
              </div>
            ))}
          </div>
        ) : entries.length === 0 ? (
          <div className="leaderboard-empty">No entries yet.</div>
        ) : (
          entries.map((entry, idx) => (
            <div key={`${entry.nickname}-${idx}`} className="leaderboard-row" role="row">
              <div className="leaderboard-col rank" role="cell">{idx + 1}</div>
              <div className="leaderboard-col name" role="cell">{entry.nickname}</div>
              <div className="leaderboard-col score" role="cell">{entry.cumulative_score}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Leaderboard;


