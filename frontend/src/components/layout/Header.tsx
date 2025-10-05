import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setIsMenuOpen(false);
    navigate('/login');
  };

  const handleNavClick = (sectionId: string) => {
    navigate('/');
    setTimeout(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
    setIsMenuOpen(false);
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-section">
          <button onClick={() => handleNavClick('home')} className="logo">
            <div className="bus-icon">🚌</div>
            <span className="logo-text">BussinIt</span>
          </button>
        </div>
        
        <div className="header-right">
          <nav className="nav-desktop"> 
            <ul className="nav-list">
              <li><button onClick={() => handleNavClick('home')} className="nav-link">Home</button></li>
              <li><button onClick={() => handleNavClick('features')} className="nav-link">Features</button></li>
              <li><button onClick={() => handleNavClick('about')} className="nav-link">About</button></li>
              <li><button onClick={() => handleNavClick('contact')} className="nav-link">Contact</button></li>
              <li><Link to="/leaderboard" className="nav-link">Leaderboard</Link></li>
            </ul>
          </nav>

          <div className="header-actions">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard">
                  <button className="btn-primary">Dashboard</button>
                </Link>
                <Link to="/account">
                  <button className="btn-secondary">My Account</button>
                </Link>
                <button className="btn-secondary" onClick={handleLogout}>Logout</button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <button className="btn-secondary">Login</button>
                </Link>
                <Link to="/register">
                  <button className="btn-primary">Register</button>
                </Link>
              </>
            )}
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
          <li><button onClick={() => handleNavClick('home')} className="mobile-nav-link">Home</button></li>
          <li><button onClick={() => handleNavClick('features')} className="mobile-nav-link">Features</button></li>
          <li><button onClick={() => handleNavClick('about')} className="mobile-nav-link">About</button></li>
          <li><button onClick={() => handleNavClick('contact')} className="mobile-nav-link">Contact</button></li>
          <li><Link to="/leaderboard" className="mobile-nav-link" onClick={toggleMenu}>Leaderboard</Link></li>
          {isAuthenticated ? (
            <>
              <li><Link to="/dashboard" className="mobile-nav-link" onClick={toggleMenu}>Dashboard</Link></li>
              <li><Link to="/leaderboard" className="mobile-nav-link" onClick={toggleMenu}>Leaderboard</Link></li>
              <li><Link to="/add-friend" className="mobile-nav-link" onClick={toggleMenu}>Add Friend</Link></li>
              <li><Link to="/friend-requests" className="mobile-nav-link" onClick={toggleMenu}>Requests</Link></li>
              <li><Link to="/account" className="mobile-nav-link" onClick={toggleMenu}>My Account</Link></li>
              <li><button className="mobile-nav-link" onClick={handleLogout}>Logout</button></li>
            </>
          ) : (
            <>
              <li><Link to="/login" className="mobile-nav-link" onClick={toggleMenu}>Login</Link></li>
              <li><Link to="/register" className="mobile-nav-link" onClick={toggleMenu}>Register</Link></li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
};

export default Header;
