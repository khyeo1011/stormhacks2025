import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Features.css';

const Features: React.FC = () => {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Predictions',
      description: 'We use the latest in AI technology to predict bus delays with high accuracy.',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      icon: '⏰',
      title: 'Real-Time Updates',
      description: 'Get instant notifications about delays, cancellations, and schedule changes. Never be caught off guard again.',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
    },
    {
      icon: '🗺️',
      title: 'Smart Routing',
      description: 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Quisquam, quos.',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    },
    {
      icon: '📱',
      title: 'Mobile Friendly',
      description: 'Optimized for all devices with an intuitive interface. Check predictions on the go with our responsive design.',
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
    },
    {
      icon: '🚌',
      title: 'Lorem Ipsum',
      description: 'dolor sit amet consectetur adipisicing elit. Quisquam, quos.',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    },
    {
      icon: '👥',
      title: 'Collaborative',
      description: 'You can compete with your friends to see who can predict the most accurate delays.',
      gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
    }
  ];

  return (
    <section className="features" id="features">
      <div className="features-container">
        <div className="features-header">
          <h2 className="features-title">
            Why Choose <span className="gradient-text">BussinIt?</span>
          </h2>
          <p className="features-description">
            Our comprehensive platform combines cutting-edge technology with user-friendly design 
            to revolutionize your daily commute experience.
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="feature-card"
              style={{ '--delay': `${index * 0.1}s` } as React.CSSProperties}
            >
              <div className="feature-icon" style={{ background: feature.gradient }}>
                <span className="icon-emoji">{feature.icon}</span>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="features-cta">
          <div className="cta-content">
            <h3 className="cta-title">Ready to Transform Your Commute?</h3>
            <p className="cta-description">
              Join thousands of users who have already made their daily travel more predictable and stress-free.
            </p>
            <button className="btn-cta" onClick={() => navigate('/register')}>
              <span>Get Started Today</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
