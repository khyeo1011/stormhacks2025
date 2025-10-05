# Email Configuration Setup

This document explains how to configure email functionality for the BussinIt application.

## Environment Variables

Add the following environment variables to your `.env` file or set them in your deployment environment:

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
CONTACT_EMAIL=support@stormhack.com
```

## Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password as `MAIL_PASSWORD`

## Alternative Email Providers

### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

### Yahoo Mail
```bash
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=true
```

### Custom SMTP Server
```bash
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
```

## Features Implemented

### 1. Contact Form
- Users can submit contact messages through the website
- Form validation on both frontend and backend
- Email notifications sent to support team
- Success/error feedback to users

### 2. Welcome Emails
- Automatic welcome emails for new users
- Can be triggered during user registration

### 3. Prediction Notifications
- Email notifications when predictions are resolved
- Includes results and points earned

## Testing Email Functionality

1. **Test Contact Form**:
   ```bash
   curl -X POST http://localhost:8000/contact/send \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","message":"Test message"}'
   ```

2. **Test Email Service**:
   ```bash
   curl -X GET http://localhost:8000/contact/test
   ```

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Check if 2FA is enabled
   - Verify app password is correct
   - Ensure "Less secure app access" is enabled (not recommended)

2. **Connection Timeout**:
   - Check firewall settings
   - Verify SMTP server and port
   - Try different TLS/SSL settings

3. **Email Not Sending**:
   - Check server logs for detailed error messages
   - Verify all environment variables are set
   - Test with a simple email client first

### Debug Mode

To enable detailed email logging, add this to your Flask app configuration:

```python
app.config['MAIL_DEBUG'] = True
```

## Security Notes

- Never commit email credentials to version control
- Use environment variables for all sensitive data
- Consider using a dedicated email service like SendGrid or Mailgun for production
- Implement rate limiting for contact forms to prevent spam
