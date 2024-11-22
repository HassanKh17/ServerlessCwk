import datetime
from email.mime.text import MIMEText
import os
import logging
import requests
import azure.functions as func
import pyodbc
from azure.communication.email import EmailClient
from azure.storage.queue import QueueClient

# Environment variables for Computer Vision and SQL
COMPUTER_VISION_ENDPOINT = os.getenv("COMPUTER_VISION_ENDPOINT")
COMPUTER_VISION_KEY = os.getenv("COMPUTER_VISION_KEY")
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")


app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="capturedframes/{name}", connection="AzureWebJobsLicenseplateimgs_STORAGE")
def blob_trigger(myblob: func.InputStream):
    logging.info(f"Processing blob: {myblob.name}, Size: {myblob.length} bytes")

    # Read image data
    image_data = myblob.read()

    # Send to Azure Computer Vision API
    ocr_url = f"{COMPUTER_VISION_ENDPOINT}/vision/v3.2/ocr"
    headers = {
        'Ocp-Apim-Subscription-Key': COMPUTER_VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }
    response = requests.post(ocr_url, headers=headers, data=image_data)
    response.raise_for_status()
    ocr_result = response.json()

    # Extract license plates
    license_plates = []
    for region in ocr_result.get("regions", []):
        for line in region.get("lines", []):
            license_plate_text = " ".join([word["text"] for word in line["words"]])
            license_plates.append(license_plate_text)

    logging.info(f"Detected License Plates: {license_plates}")

    # Store license plates in SQL Database
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD}"
    )
    conn = None
    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        for plate in license_plates:
            try:
                # Insert the detected plate into the database
                cursor.execute(
                    "INSERT INTO DetectedPlates (LicensePlate, DetectionTime) VALUES (?, GETDATE())",
                    plate
                )
                logging.info(f"Inserted license plate {plate} into DetectedPlates table.")

                # Check permit status in the database
                cursor.execute(
                    "SELECT PermitStatus, ExpirationTime FROM ParkingPermits WHERE LicensePlate = ?",
                    plate
                )
                row = cursor.fetchone()
                if row:
                    status, expiration = row
                    if status == "Active" and expiration > datetime.datetime.now():
                        logging.info(f"Parking is valid for plate: {plate}")
                    else:
                        logging.info(f"Parking violation detected for plate: {plate}")
                        send_email_alert_acs(plate)
                else:
                    logging.info(f"No permit found for plate: {plate}")
                    send_email_alert_acs(plate)
            except Exception as ex:
                logging.error(f"Error while processing plate {plate}: {ex}")
        
        # Commit all changes to the database
        conn.commit()

    except Exception as ex:
        logging.error(f"Failed to connect to SQL Database or process plates: {ex}")
    finally:
        if conn:
            conn.close()
       

def send_email_alert_acs(license_plate):
    """
    Send an email alert for parking violations using Azure Communication Services.
    """
    try:
       
        connection_string = "endpoint=https://violation-alert.uk.communication.azure.com/;accesskey=CQ6WFGZtGXPRX459IrgHYVPaZOWYjfnitQt7DrGIhjZ0HCHQ4lMXJQQJ99AKACULyCplvV7KAAAAAZCSb1c3"

        # Initialize the EmailClient
        client = EmailClient.from_connection_string(connection_string)

        # Define the email message
        message = {
            "senderAddress": "DoNotReply@0d97ba67-2b4d-45a1-97c7-d639b57f5ba5.azurecomm.net",
            "recipients": {
                "to": [
                    {"address": "sc22hkar@leeds.ac.uk"}
                ]
            },
            "content": {
                "subject": f"Parking Violation Detected for License Plate: {license_plate}",
                "plainText": (
                    f"Dear Admin,\n\n"
                    f"A parking violation has been detected for the license plate: {license_plate}.\n"
                    f"Please take necessary action.\n\n"
                    f"Best regards,\n"
                    f"License Plate Monitoring System"
                ),
                "html": f"""
                <html>
                    <body>
                        <h1>Parking Violation Detected</h1>
                        <p>License Plate: <strong>{license_plate}</strong></p>
                        <p>Please take necessary action.</p>
                        <p>Best regards,</p>
                        <p>License Plate Monitoring System</p>
                    </body>
                </html>
                """
            }
        }

        # Send the email
        poller = client.begin_send(message)
        result = poller.result()
        if isinstance(result, dict):
            logging.info(f"Email sent successfully: {result.get('id', 'unknown')}")
        else:
            logging.info(f"Email sent successfully: {result.message_id}")

    except Exception as ex:
        logging.error(f"Failed to send email: {ex}")\



@app.route(route="request-permit", methods=["POST"])
def request_permit(req: func.HttpRequest) -> func.HttpResponse:
    """
    Allow users to request a parking permit by entering their license plate and expiration date.
    """
    try:
        # Parse the incoming request
        data = req.get_json()

        license_plate = data.get("license_plate")
        expiration_date = data.get("expiration_date")  # Expecting "YYYY-MM-DD" format

        if not license_plate or not expiration_date:
            return func.HttpResponse(
                "License plate and expiration date are required.",
                status_code=400
            )

        # Validate the expiration date
        try:
            expiration_datetime = datetime.datetime.strptime(expiration_date, "%Y-%m-%d")
            if expiration_datetime <= datetime.datetime.now():
                return func.HttpResponse(
                    "Expiration date must be in the future.",
                    status_code=400
                )
        except ValueError:
            return func.HttpResponse(
                "Invalid expiration date format. Use 'YYYY-MM-DD'.",
                status_code=400
            )

        # Store the permit request in the database
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            f"UID={SQL_USERNAME};"
            f"PWD={SQL_PASSWORD}"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Check if the license plate already has an active permit
        cursor.execute(
            "SELECT PermitStatus, ExpirationTime FROM ParkingPermits WHERE LicensePlate = ?",
            license_plate
        )
        row = cursor.fetchone()
        if row and row[0] == "Active" and row[1] > datetime.datetime.now():
            conn.close()
            return func.HttpResponse(
                "This license plate already has an active permit.",
                status_code=400
            )

        # Insert the new permit request
        cursor.execute(
            """
            INSERT INTO ParkingPermits (LicensePlate, ExpirationTime, PermitStatus)
            VALUES (?, ?, ?)
            """,
            license_plate, expiration_datetime, "Active"
        )
        conn.commit()
        conn.close()

        return func.HttpResponse(
            f"Permit request for license plate '{license_plate}' has been successfully submitted. Permit is valid until {expiration_date}.",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error in request-permit function: {e}")
        return func.HttpResponse(
            "An error occurred while processing the permit request.",
            status_code=500
        )
