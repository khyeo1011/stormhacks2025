import React from 'react';
import './About.css';

const About: React.FC = () => {
  return (
    <section className="about" id="about">
      <div className="about-container">
        <div className="about-content">
          <h2 className="about-title">
            <span className="gradient-text">About BussinIt</span>
          </h2>
          
          <p className="about-description">
            We're passionate about improving public transportation through innovative 
            prediction technology. Our platform helps commuters make informed decisions 
            and contributes to better bus service reliability across cities.
          </p>
          
          <div className="about-stats">
            <div className="stat-item">
              <div className="stat-number">2023</div>
              <div className="stat-label">Founded</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">5</div>
              <div className="stat-label">Team Members</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">50+</div>
              <div className="stat-label">Cities</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">1M+</div>
              <div className="stat-label">Predictions Made</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
