import os
from flask import current_app
from flask_mail import Mail, Message
from datetime import datetime

# Initialize mail instance
mail = Mail()

def init_email_service(app):
    """Initialize email service with Flask app"""
    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
    
    mail.init_app(app)

def send_contact_email(name, email, message):
    """Send contact form email"""
    try:
        # Create message
        msg = Message(
            subject=f'Contact Form Submission from {name}',
            recipients=[os.getenv('CONTACT_EMAIL', 'support@stormhack.com')],
            reply_to=email
        )
        
        # Email body
        msg.body = f"""
Contact Form Submission

Name: {name}
Email: {email}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message:
{message}

---
This message was sent from the BussinIt contact form.
        """
        
        # HTML version
        msg.html = f"""
        <html>
        <body>
            <h2>Contact Form Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Message:</strong></p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
            </div>
            <hr>
            <p><em>This message was sent from the BussinIt contact form.</em></p>
        </body>
        </html>
        """
        
        # Send email
        mail.send(msg)
        return True, "Email sent successfully"
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False, f"Failed to send email: {str(e)}"

def send_welcome_email(user_email, user_name):
    """Send welcome email to new users"""
    try:
        msg = Message(
            subject='Welcome to BussinIt!',
            recipients=[user_email]
        )
        
        msg.body = f"""
Welcome to BussinIt, {user_name}!

Thank you for joining our bus prediction game. You can now:
- Make predictions about bus delays
- Compete with friends
- Track your accuracy score
- Climb the leaderboard

Get started by making your first prediction!

Best regards,
The BussinIt Team
        """
        
        msg.html = f"""
        <html>
        <body>
            <h2>Welcome to BussinIt, {user_name}!</h2>
            <p>Thank you for joining our bus prediction game. You can now:</p>
            <ul>
                <li>Make predictions about bus delays</li>
                <li>Compete with friends</li>
                <li>Track your accuracy score</li>
                <li>Climb the leaderboard</li>
            </ul>
            <p>Get started by making your first prediction!</p>
            <br>
            <p>Best regards,<br>The BussinIt Team</p>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True, "Welcome email sent successfully"
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email: {str(e)}")
        return False, f"Failed to send welcome email: {str(e)}"

def send_prediction_notification(user_email, prediction_result):
    """Send notification when prediction is resolved"""
    try:
        msg = Message(
            subject='Your Bus Prediction Result',
            recipients=[user_email]
        )
        
        status = "correct" if prediction_result['correct'] else "incorrect"
        points = prediction_result.get('points_earned', 0)
        
        msg.body = f"""
Prediction Result Update

Your prediction for {prediction_result.get('route_name', 'Unknown Route')} was {status}!

Points earned: {points}
New total score: {prediction_result.get('new_total_score', 0)}

Keep predicting to climb the leaderboard!

Best regards,
The BussinIt Team
        """
        
        msg.html = f"""
        <html>
        <body>
            <h2>Prediction Result Update</h2>
            <p>Your prediction for <strong>{prediction_result.get('route_name', 'Unknown Route')}</strong> was <strong>{status}</strong>!</p>
            <div style="background-color: {'#d4edda' if prediction_result['correct'] else '#f8d7da'}; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p><strong>Points earned:</strong> {points}</p>
                <p><strong>New total score:</strong> {prediction_result.get('new_total_score', 0)}</p>
            </div>
            <p>Keep predicting to climb the leaderboard!</p>
            <br>
            <p>Best regards,<br>The BussinIt Team</p>
        </body>
        </html>
        """
        
        mail.send(msg)
        return True, "Notification sent successfully"
        
    except Exception as e:
        current_app.logger.error(f"Failed to send prediction notification: {str(e)}")
        return False, f"Failed to send prediction notification: {str(e)}"
