# Telegram Chat History ETL

This project is an ETL (Extract, Transform, Load) pipeline for Telegram chat history. It extracts messages from specified Telegram chats, processes them, and loads them into Google BigQuery tables.

## Features

- Supports two modes: daily updates and historical backloading
- Configurable through environment variables
- Automatically handles new users and chats
- Efficiently processes only new data
- Stores chat history, chat info, and user info in separate BigQuery tables

## Prerequisites
- Python 3.10+
- Google Cloud account with BigQuery enabled
- Telegram API credentials (API ID and API Hash)

## Installation

1. Clone this repository:

```bash
    git clone https://github.com/ada1312/telegram-chat-history-etl.git
    cd telegram-chat-history-etl
```

2. Install the required packages:

```bash
    pip install -r requirements.txt
```

3. Set up your environment variables in a .env file:
- API_ID=your_telegram_api_id
- API_HASH=your_telegram_api_hash
- PHONE_NUMBER=your_telegram_phone_number
- CHAT_USERNAME=username_of_chats
- SAMPLE_SIZE=number_for_specific_size_NONE_for_all_histroy
- PROJECT_ID=your_google_cloud_project_id
- DATASET_ID=your_bigquery_dataset_id
- TABLE_CHAT_CONFIG=chat_config
- TABLE_CHAT_HISTORY=chat_history
- TABLE_CHAT_INFO=chat_info
- TABLE_USER_INFO=user_info
- LOGGING_LEVEL=INFO
- MODE="day_ago" # 'day_ago' or 'backload'
- BACKLOAD_START_DATE=YYYY-MM-DD
- BACKLOAD_END_DATE=YYYY-MM-DD
- TELEGRAM_SESSION_STRING: The session string generated in step below


## Usage
The script can be run in two modes: day_ago and backload.

## Daily Mode
This mode processes data for the previous day.

    ```bash
    python main.py day_ago

    ```
Set the following environment variables:

    ```bash
    MODE=day_ago
    ```

## Backload Mode
This mode processes historical data for a specified date range.

    ```bash
    python main.py backload --start_date YYYY-MM-DD --end_date YYYY-MM-DD

    ```
Set the following environment variables:

    ```bash
    MODE=backload
    BACKLOAD_START_DATE=2023-01-01
    BACKLOAD_END_DATE=2023-12-31
    ```

##  Recent Mode
This mode process historical data for specific minutes that are setu up via chrom job. 

    ```bash
    python main.py recent --minutes 30

    ```
Set the following environment variables:

    ```bash
    MODE=recent
    ```

## BigQuery Schema
The script expects the following tables in your BigQuery dataset:

1. chat_config:
```bash
    bq mk --table your_dataset_id.chat_config \
    id:STRING,username:STRING,dates_to_load:DATE
```

2. chat_history:
```bash
    bq mk --table your_dataset_id.chat_history \
    id:INTEGER,date:FLOAT,from_user:INTEGER,text:STRING,sender:INTEGER,chat_id:INTEGER,is_reply:BOOLEAN,views:INTEGER,forwards:INTEGER,replies:STRING,buttons:STRING,media:STRING,entities:STRING,mentioned:BOOLEAN,post_author:STRING,edit_date:TIMESTAMP,via_bot:STRING,reply_to:RECORD,reactions:STRING,fwd_from:STRING,grouped_id:STRING,action:STRING,reply_to.reply_to_msg_id:INTEGER,reply_to.reply_to_peer_id:STRING

```


3. chat_info
```bash
    bq mk --table your_dataset_id.chat_info \
    id:INTEGER,name:STRING,username:STRING,description:STRING,members_count:STRING,linked_chat_id:STRING

```

4. user_info
```bash
    bq mk --table your_dataset_id.user_info \
    id:INTEGER,first_name:STRING,last_name:STRING,username:STRING,phone:INTEGER,bot:BOOLEAN,verified:BOOLEAN,restricted:BOOLEAN,scam:BOOLEAN,fake:BOOLEAN,access_hash:INTEGER,bio:STRING,bot_info:STRING
```

## Project Structure

main.py: Main script that orchestrates the data collection process
bigquery_loader.py: Handles uploading data to BigQuery
chat_config.py: Manages chat configuration data in BigQuery
chat_history.py: Retrieves chat history from Telegram
chat_info.py: Retrieves chat information from Telegram
user_info.py: Retrieves user information from Telegram
data_processor.py: Processes and manages the data flow

## Data Processing
The DataProcessor class in data_processor.py handles the main logic for processing chat data:

Initializes by fetching existing users and chats from BigQuery
Processes each chat, retrieving chat info and history
Manages new users and chats
Uploads processed data to BigQuery

## User Information
The get_user_info function in user_info.py retrieves detailed information about Telegram users, including:

User ID, name, username, phone number
Bot status, verification status
Restricted, scam, and fake flags
Access hash, bio, and bot info

## Deployment

This script is designed to be run as a scheduled job in Google Cloud Run. Follow these steps to deploy the application:

### Prerequisites

- Docker installed on your local machine
- Google Cloud SDK installed and configured
- Terraform installed
- Access to a Google Cloud project with necessary APIs enabled (Cloud Run, Container Registry, BigQuery, Secret Manager)

### Deployment Process

1. **Build and Push Docker Image**

   Build the Docker image locally:
```bash
   docker build -t gcr.io/container-testing-381309/telegram_update_etl:latest .
   ```
    Push the image to Google Container Registry:

```bash
   docker push gcr.io/container-testing-381309/telegram_update_etl:latest
   ```
   Alternatively, use Cloud Build:
```bash
   gcloud builds submit --config=cloudbuild.yaml .
   ```

2. **Generate Telegram Session String**
Run the following Python script to generate a session string:

```python
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = 'your_api_id'
api_hash = 'your_api_hash'
phone_number = 'your_phone_number'

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start(phone=phone_number)
    print(client.session.save())
```
Save the output string securely.

3. **Apply Terraform Configuration Initialize Terraform**

```bash
terraform init
```
Plan your changes:
```bash
terraform plan -var="telegram_session_string=your_session_string_here"
```
Apply the changes:
```bash
terraform apply -var="telegram_session_string=your_session_string_here"
```
Or use a .tfvars file for sensitive information:
```bash
terraform apply -var-file="secrets.tfvars"
```