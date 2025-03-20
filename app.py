from flask import Flask, render_template, request, jsonify
import os
import shutil
import logging
import traceback 
from google_sheets import add_rsvp_to_sheet, get_guest_list

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set the maximum file size for uploads (e.g., 50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def index():
    # Default route shows general version with default video
    # Ensure the videos directory exists
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')
    
    # Check if video.mp4 exists in the current directory and copy it to static/videos if needed
    if os.path.exists('video.mp4') and not os.path.exists('static/videos/video.mp4'):
        shutil.copy('video.mp4', 'static/videos/video.mp4')
        
    return render_template('index.html', family_video='video.mp4')

@app.route('/Sangeet')
def sangeet_page():
    # Ensure the videos directory exists
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')
    
    # Custom message for the Sangeet page with proper formatting
    custom_message = {
        'heading': 'Dance to the beat',
        'description': "You've asked, so here it is-rhythm of the life.\n\nBefore we tie the knot, let's celebrate with a night full of music, dance, and unforgettable moments! Join us for an evening of joy, laughter, and dazzling performances in Pilot Point, Texas!!",
        'custom_date': "April 11th, 2025",
        'custom_time': "From 5 PM to 10 PM",
        'custom_dinner_time': "Dinner 7:00 PM",
        'custom_rsvp_message': "If you can make it to our Sangeet, please fill in your details below so we can reserve a spot for you on the dance floor. 🎶💃🕺"
    }
    
    # Pass the custom spreadsheet ID for Sangeet RSVPs
    sangeet_sheet_id = "1Ux3gEGVr6Kg90_yh021nLg6FOzwAlOx9JiBCktOSHTo"
    
    return render_template('index.html', family_video='sangeeth.png', is_image=True, 
                           custom_message=custom_message, sheet_id=sangeet_sheet_id)

@app.route('/Bheemineni')
def bheemineni_page():
    # Ensure the videos directory exists
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')
    
    return render_template('index.html', family_video='Bheemineni_video.mp4')
    
@app.route('/siddana')
def siddana_page():
    # Ensure the videos directory exists
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')
    
    return render_template('index.html', family_video='siddana_video.mp4')

@app.route('/submit_rsvp', methods=['POST'])
def submit_rsvp():
    try:
        print("======== RSVP SUBMISSION RECEIVED ========")
        logger.info("======== RSVP SUBMISSION RECEIVED ========")
        
        # Debug raw request
        logger.debug(f"Request content type: {request.content_type}")
        logger.debug(f"Request data: {request.data}")
        print(f"REQUEST DATA: {request.data}")
        
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received in request")
            logger.debug(f"Request headers: {dict(request.headers)}")
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        logger.debug(f"Parsed JSON data: {data}")
        print(f"PARSED JSON: {data}")
        
        family_name = data.get('familyName')
        guest_count = data.get('guestCount')
        sheet_id = data.get('sheetId')
        
        logger.info(f"Processing RSVP for: {family_name}, Guests: {guest_count}")
        print(f"PROCESSING: {family_name}, {guest_count}")
        
        if not family_name or not guest_count:
            logger.error("Missing required fields")
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Print the contents of credentials.json (without sensitive data)
        try:
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                # Print metadata without revealing private keys
                print(f"Credentials file contains keys: {list(creds.keys())}")
                print(f"Project ID: {creds.get('project_id')}")
                print(f"Client Email: {creds.get('client_email')}")
                # Check if file is properly formatted JSON
                print(f"Credentials file is valid JSON: {bool(creds)}")
        except Exception as e:
            print(f"ERROR reading credentials file: {str(e)}")
            return jsonify({"success": False, "error": f"Credentials file error: {str(e)}"}), 500
        
        # Add to Google Sheet - with better error handling
        try:
            logger.info("Attempting to add to Google Sheet")
            # Pass the sheet_id if provided, otherwise use default
            result = add_rsvp_to_sheet(family_name, guest_count, sheet_id)
            logger.info(f"Google Sheet result: {result}")
            return jsonify({"success": True if result.get('success') else False, 
                           "error": result.get('error', None)})
        except Exception as e:
            logger.exception("Error adding to Google Sheet")
            return jsonify({"success": False, "error": f"Google Sheets error: {str(e)}"}), 500
            
    except Exception as e:
        logger.exception("Unexpected error in submit_rsvp")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/debug')
def debug_info():
    """Route for debugging server information"""
    try:
        static_files = os.listdir('static')
        css_files = os.listdir('static/css') if os.path.exists('static/css') else []
        js_files = os.listdir('static/js') if os.path.exists('static/js') else []
        image_files = os.listdir('static/images') if os.path.exists('static/images') else []
        video_files = os.listdir('static/videos') if os.path.exists('static/videos') else []
        
        return jsonify({
            'success': True,
            'static_files': static_files,
            'css_files': css_files,
            'js_files': js_files,
            'image_files': image_files,
            'video_files': video_files,
            'env': {k: v for k, v in os.environ.items()},
            'working_dir': os.getcwd()
        })
    except Exception as e:
        logger.exception("Error in debug endpoint")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/test')
def test_form():
    return open('test_form.html').read()

@app.route('/guest-list')
def guest_list():
    """Display the guest lists for both Wedding and Sangeet events."""
    # Define both sheet IDs
    wedding_sheet_id = '1zlnCo2WRxWDxCnbditnx5tAylcmXrI2w0gCDyq5bjXg'
    sangeet_sheet_id = '1Ux3gEGVr6Kg90_yh021nLg6FOzwAlOx9JiBCktOSHTo'
    
    # Get data for both sheets
    try:
        wedding_data = get_guest_list(wedding_sheet_id)
        sangeet_data = get_guest_list(sangeet_sheet_id)
        
        return render_template(
            'guest_list.html',
            wedding_data=wedding_data,
            sangeet_data=sangeet_data,
            wedding_sheet_id=wedding_sheet_id,
            sangeet_sheet_id=sangeet_sheet_id
        )
    except Exception as e:
        logger.exception(f"Error in guest list page: {str(e)}")
        return f"Error loading guest lists: {str(e)}", 500

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(host='0.0.0.0', port=5555, debug=True) 