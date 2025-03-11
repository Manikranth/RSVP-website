from flask import Flask, render_template, request, jsonify
import os
import shutil
import logging
from google_sheets import add_rsvp_to_sheet

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
        print("======== RSVP SUBMISSION RECEIVED ========")  # Console print for visibility
        logger.info("======== RSVP SUBMISSION RECEIVED ========")
        
        # Debug raw request
        logger.debug(f"Request content type: {request.content_type}")
        logger.debug(f"Request data: {request.data}")
        print(f"REQUEST DATA: {request.data}")  # Console print for visibility
        
        data = request.get_json()
        
        if not data:
            logger.error("No JSON data received in request")
            logger.debug(f"Request headers: {dict(request.headers)}")
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        logger.debug(f"Parsed JSON data: {data}")
        print(f"PARSED JSON: {data}")  # Console print for visibility
        
        family_name = data.get('familyName')
        guest_count = data.get('guestCount')
        
        logger.info(f"Processing RSVP for: {family_name}, Guests: {guest_count}")
        print(f"PROCESSING: {family_name}, {guest_count}")  # Console print for visibility
        
        if not family_name or not guest_count:
            logger.error("Missing required fields")
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Add to Google Sheet - with better error handling
        try:
            logger.info("Attempting to add to Google Sheet")
            result = add_rsvp_to_sheet(family_name, guest_count)
            logger.info(f"Google Sheet result: {result}")
            return jsonify({"success": True})
        except Exception as e:
            logger.exception("Error adding to Google Sheet")
            return jsonify({"success": False, "error": f"Google Sheets error: {str(e)}"}), 500
            
    except Exception as e:
        logger.exception("Unexpected error in submit_rsvp")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/test')
def test_form():
    return open('test_form.html').read()

if __name__ == '__main__':
    logger.info("Starting the Flask application")
    app.run(host='0.0.0.0', port=5555, debug=True) 