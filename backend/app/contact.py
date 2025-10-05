from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from .email_service import send_contact_email
import re

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_contact_form(name, email, message):
    """Validate contact form data"""
    errors = []
    
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")
    
    if not email or not validate_email(email):
        errors.append("Please provide a valid email address")
    
    if not message or len(message.strip()) < 10:
        errors.append("Message must be at least 10 characters long")
    
    return errors

@contact_bp.route('/send', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_contact_message():
    """Handle contact form submission"""
    try:
        # Handle preflight request
        if request.method == 'OPTIONS':
            return jsonify({'message': 'OK'}), 200
        
        # Get form data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        
        # Validate form data
        errors = validate_contact_form(name, email, message)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Send email
        success, result_message = send_contact_email(name, email, message)
        
        if success:
            return jsonify({
                'message': 'Contact message sent successfully',
                'status': 'success'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send message',
                'details': result_message
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@contact_bp.route('/test', methods=['GET'])
@cross_origin()
def test_contact_endpoint():
    """Test endpoint to verify contact service is working"""
    return jsonify({
        'message': 'Contact service is working',
        'status': 'success',
        'endpoints': {
            'send': '/contact/send (POST)',
            'test': '/contact/test (GET)'
        }
    }), 200
