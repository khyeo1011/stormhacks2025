import React, { useState } from 'react';
import './Header.css';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section">
          <a href="#home" className="logo">
            <div className="bus-icon">🚌</div>
            <span className="logo-text">BussinIt</span>
          </a>
        </div>
        
        <div className="header-right">
          <nav className="nav-desktop"> 
            <ul className="nav-list">
              <li><a href="#home" className="nav-link">Home</a></li>
              <li><a href="#features" className="nav-link">Features</a></li>
              <li><a href="#about" className="nav-link">About</a></li>
              <li><a href="#contact" className="nav-link">Contact</a></li>
            </ul>
          </nav>

          <div className="header-actions">
            <button className="btn-primary">Get Started</button>
          </div>
        </div>

        <button className="menu-toggle" onClick={toggleMenu} aria-label="Toggle menu">
          <span className={`hamburger ${isMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      </div>

      {/* Mobile Menu */}
      <nav className={`nav-mobile ${isMenuOpen ? 'open' : ''}`}>
        <ul className="mobile-nav-list">
          <li><a href="#home" className="mobile-nav-link" onClick={toggleMenu}>Home</a></li>
          <li><a href="#features" className="mobile-nav-link" onClick={toggleMenu}>Features</a></li>
          <li><a href="#about" className="mobile-nav-link" onClick={toggleMenu}>About</a></li>
          <li><a href="#contact" className="mobile-nav-link" onClick={toggleMenu}>Contact</a></li>
          <li className="mobile-cta">
            <button className="btn-primary-mobile" onClick={toggleMenu}>Get Started</button>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
