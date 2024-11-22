# License Plate Monitoring System

The License Plate Monitoring System is a serverless application designed to automate license plate detection, validate parking permits, and notify administrators of parking violations using Azure's cloud services.

---

## Table of Contents

- [Overview](#overview)
- [Azure Resoures](#architecture)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Setup and Deployment](#setup-and-deployment)
- [How to Run](#how-to-run)
- [How to Use](#how-to-use)
- [Environment Variables](#environment-variables)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)

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
