import logging
import datetime
import gspread
from google.oauth2.service_account import Credentials

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Spreadsheet details
DEFAULT_SPREADSHEET_ID = '1zlnCo2WRxWDxCnbditnx5tAylcmXrI2w0gCDyq5bjXg'
SHEET_NAME = 'Sheet1'

def add_rsvp_to_sheet(family_name, guest_count, custom_sheet_id=None):
    """Adds RSVP information to Google Sheet using gspread."""
    try:
        logger.info(f"Adding RSVP for {family_name} with {guest_count} guests")
        
        # Use custom sheet ID if provided, otherwise use default
        spreadsheet_id = custom_sheet_id if custom_sheet_id else DEFAULT_SPREADSHEET_ID
        logger.info(f"Using spreadsheet ID: {spreadsheet_id}")
        
        # Load credentials and authorize gspread
        creds = Credentials.from_service_account_file(
            "credentials.json", 
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        
        # Test if we can access any spreadsheets (permission check)
        try:
            all_spreadsheets = client.list_spreadsheet_files()
            logger.info(f"Found {len(all_spreadsheets)} spreadsheets accessible to this service account")
            for sheet in all_spreadsheets:
                logger.info(f"  - {sheet['name']} (ID: {sheet['id']})")
        except Exception as e:
            logger.error(f"ERROR listing spreadsheets: {str(e)}")
        
        # Open the spreadsheet by ID
        logger.info(f"Opening spreadsheet with ID: {spreadsheet_id}")
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            logger.info(f"Successfully opened spreadsheet: {spreadsheet.title}")
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"ERROR: Spreadsheet with ID {spreadsheet_id} not found!")
            return {"success": False, "error": "Spreadsheet not found"}
        except Exception as e:
            logger.error(f"ERROR opening spreadsheet: {str(e)}")
            return {"success": False, "error": f"Error opening spreadsheet: {str(e)}"}
        
        # Get the worksheet
        try:
            sheet = spreadsheet.worksheet(SHEET_NAME)
            logger.info(f"Successfully opened worksheet: {SHEET_NAME}")
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"ERROR: Worksheet '{SHEET_NAME}' not found!")
            return {"success": False, "error": "Worksheet not found"}
        except Exception as e:
            logger.error(f"ERROR opening worksheet: {str(e)}")
            return {"success": False, "error": f"Error opening worksheet: {str(e)}"}
        
        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append the data as a new row
        logger.info(f"Appending data: {family_name}, {guest_count}, {timestamp}")
        try:
            row = [family_name, guest_count, timestamp]
            result = sheet.append_row(row)
            logger.info(f"Row append result: {result}")
            return {"success": True}
        except Exception as e:
            logger.error(f"ERROR appending row: {str(e)}")
            return {"success": False, "error": f"Error adding data: {str(e)}"}
            
    except Exception as e:
        logger.exception(f"ERROR in add_rsvp_to_sheet: {str(e)}")
        return {"success": False, "error": str(e)} 