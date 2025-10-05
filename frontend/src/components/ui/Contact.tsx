import React, { useState, useRef } from 'react';
import './Contact.css';

const Contact: React.FC = () => {
  const [copiedItem, setCopiedItem] = useState<string | null>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItem(type);
      setTimeout(() => setCopiedItem(null), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    const button = buttonRef.current;
    if (!button) return;
    
    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    button.style.setProperty('--mouse-x', `${x}px`);
    button.style.setProperty('--mouse-y', `${y}px`);
  };

  const handleMouseLeave = () => {
    const button = buttonRef.current;
    if (!button) return;
    
    button.style.setProperty('--mouse-x', '50%');
    button.style.setProperty('--mouse-y', '50%');
  };

  return (
    <section className="contact">
      <div className="contact-container">
        <h2>Contact Us</h2>
        <p>Get in touch with us for any questions or support.</p>
        
        <div className="contact-info">
          <div className="contact-item">
            <h3>📧 Email</h3>
            <p 
              className="contact-highlight clickable" 
              onClick={() => copyToClipboard('support@stormhack.com', 'email')}
              title="Click to copy"
            >
              {copiedItem === 'email' ? '✓ Copied!' : 'support@stormhack.com'}
            </p>
          </div>
          
          <div className="contact-item">
            <h3>📞 Phone</h3>
            <p 
              className="contact-highlight clickable" 
              onClick={() => copyToClipboard('+1 (555) 123-4567', 'phone')}
              title="Click to copy"
            >
              {copiedItem === 'phone' ? '✓ Copied!' : '+1 (555) 123-4567'}
            </p>
          </div>
        </div>
        
        <form className="contact-form">
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input type="text" id="name" name="name" required />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" name="email" required />
          </div>
          
          <div className="form-group">
            <label htmlFor="message">Message</label>
            <textarea id="message" name="message" rows={5} required></textarea>
          </div>
          
          <button 
            type="submit" 
            className="submit-btn"
            ref={buttonRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
          >
            Send Message
          </button>
        </form>
      </div>
    </section>
  );
};

export default Contact;
