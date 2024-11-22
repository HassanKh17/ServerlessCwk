# License Plate Monitoring System

The License Plate Monitoring System is a serverless application designed to automate license plate detection, validate parking permits, and notify administrators of parking violations using Azure's cloud services.

---

## Table of Contents

- [Overview](#overview)
- [Azure Resoures](#Azure-Resources-Visualized)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Setup and Deployment](#setup-and-deployment)
- [How to Run](#how-to-run)
- [How to Use](#how-to-use)

---

## Overview

This system is a serverless application built on Azure Functions to detect and validate license plates for a parking management system. Using Azure's Cognitive Services, SQL Database, and Communication Services, it enables automated license plate detection, permit management, and violation alerts.

---

## Azure Resources Visualized
![image](https://github.com/user-attachments/assets/ece57d7e-b89c-4339-96d9-c26ff70f666c)


---

## Key Features

- **License Plate Detection**: Extract license plate numbers from uploaded images using Azure Computer Vision OCR.
- **Parking Permit Validation**: Check if a detected license plate has an active parking permit stored in Azure SQL Database.
- **Email Alerts**: Notify administrators via Azure Communication Services when violations are detected.
- **Permit Management**: Allow users to request parking permits via an HTTP-triggered function.

---

## Technologies Used

1. **Azure Functions**:
   - Blob Trigger: Processes images uploaded to Azure Blob Storage.
   - HTTP Trigger: Handles user permit requests.

2. **Azure SQL Database**:
   - Stores license plates, permits, and logs violations.

3. **Azure Computer Vision**:
   - OCR service for extracting text (license plates) from images.

4. **Azure Communication Services**:
   - Sends email alerts for parking violations and permit confirmations.

5. **Python**:
   - Application logic written in Python using libraries such as `pyodbc` and `requests`.

6. **Azure Load Testing**:
   - Tests system performance and scalability.

---

## Setup and Deployment

### Prerequisites

- Azure account
- Python 3.8 or later
- Azure CLI
- Visual Studio Code with Azure Functions extension

### Steps

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd license-plate-functions-project
2. Install Dependencies
   ```bash 
   pip install -r requirements.txt
3. Set Up Environment Variables in local.settings.json
   ```bash
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=licenseplateimgs;AccountKey=NKZCoPXXWZBHdDbfu3Ju3NTYz/NOKDmiKs+hHD9aCANFMT9XJ51B1VIBXLLaabgVhziGmJlGKOSZ+AStfurVjw==;EndpointSuffix=core.windows.net",
       "AzureWebJobsLicenseplateimgs_STORAGE": "DefaultEndpointsProtocol=https;AccountName=licenseplateimgs;AccountKey=NKZCoPXXWZBHdDbfu3Ju3NTYz/NOKDmiKs+hHD9aCANFMT9XJ51B1VIBXLLaabgVhziGmJlGKOSZ+AStfurVjw==;EndpointSuffix=core.windows.net",
       "COMPUTER_VISION_ENDPOINT": "https://licenseplatevision.cognitiveservices.azure.com/",
       "COMPUTER_VISION_KEY": "7m7pCJK6MYOo8DrrWjkjpRfWThYbBwZHFzLbKvezuuzCpnFnnEPfJQQJ99AKACmepeSXJ3w3AAAFACOGJNyA",
       "SQL_SERVER": "serverlesscourseworkserver.database.windows.net",
       "SQL_DATABASE": "LicensePlateDB",
       "SQL_USERNAME": "sqladmin",
       "SQL_PASSWORD": "serverless!2",
       "SQL_CONNECTION_STRING": "Driver={ODBC Driver 18 for SQL Server};Server=tcp:serverlesscourseworkserver.database.windows.net,1433;Database=LicensePlateDB;Uid=sqladmin;Pwd=serverless!2;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;",
       "FUNCTIONS_WORKER_RUNTIME": "python"
     },
     "ConnectionStrings": {}
   }
4. Deploy the Azure Function App
   ```bash 
   func azure functionapp publish <license-plate-functions>
## How to Run
### Locally
1- Start the Azure Function runtime:

   ```bash
   func start
   ```
2- Test the blob-triggered function:
   Upload images to your Azure Blob Storage container.
3- Test the HTTP trigger:
   Send a POST request using the following example:
   ```bash
   Copy code
   curl -X POST -H "Content-Type: application/json" -d '{
       "license_plate": "ABC123",
       "expiration_date": "2024-12-31"
   }' http://localhost:7071/api/request-permit
   ```
### On Azure
1- Trigger Blob Function:
     -Upload an image to the `capturedframes` blob container to trigger the blob function.
   
2- Send POST Request:
     - Send a POST request to the deployed HTTP endpoint:
     
      ```bash
      POST https://<license-plate-functions>.azurewebsites.net/api/request-permit
      ```
## How to Use

### Permit Management
- Send an HTTP POST request with `license_plate` and `expiration_date` fields to request a parking permit.

### Violation Detection
- Upload images to the blob container `capturedframes`. The system will detect plates and check their validity against the database.

### Receive Notifications
- If a violation is detected, administrators will receive email alerts.

   
