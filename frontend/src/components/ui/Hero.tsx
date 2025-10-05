import React from 'react';
import { Link } from 'react-router-dom';
import './Hero.css';

const Hero: React.FC = () => {
  return (
    <section className="hero" id="home">
      <div className="hero-background">
        <div className="hero-pattern"></div>
      </div>
      
      <div className="hero-container">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              <span className="hero-gradient-text">BussinIt</span>
              </h1><h1 className="hero-title">
              Predict Bus Delays
            </h1>
            
            <p className="hero-description">
              Transform your daily commute into an exciting prediction game! 
              Use real-time transit data to forecast bus delays with friends. 
              Compete, learn, and never miss your bus again.
            </p>
            
            <div className="hero-actions">
              <Link to="/login" className="btn-primary-large">
                <span>Start Predicting</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </Link>
              <Link to="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank" rel="noopener noreferrer">
              <button className="btn-secondary-large">
          
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h8M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                
                
                <span>Watch Demo</span>
              </button>
              </Link>
            </div>
            
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">95%</div>
                <div className="stat-label">Accuracy Rate</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">10K+</div>
                <div className="stat-label">Daily Users</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">50+</div>
                <div className="stat-label">Cities Covered</div>
              </div>
            </div>
          </div>
          
          <div className="hero-visual">
            <div className="bus-illustration">
              <div className="bus-container">
                <div className="bus">
                  <div className="bus-window"></div>
                  <div className="bus-window"></div>
                  <div className="bus-door"></div>
                </div>
                <div className="road"></div>
                <div className="prediction-bubble">
                  <div className="bubble-content">
                    <div className="bubble-title">Next Bus</div>
                    <div className="bubble-time">5 min</div>
                    <div className="bubble-status on-time">On Time</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
