``` Markdown
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
    API_ID=your_telegram_api_id
    API_HASH=your_telegram_api_hash
    PHONE_NUMBER=your_telegram_phone_number
    CHAT_USERNAME=username_of_chats
    SAMPLE_SIZE=number_for_specific_size_NONE_for_all_histroy
    PROJECT_ID=your_google_cloud_project_id
    DATASET_ID=your_bigquery_dataset_id
    TABLE_CHAT_CONFIG=chat_config
    TABLE_CHAT_HISTORY=chat_history
    TABLE_CHAT_INFO=chat_info
    TABLE_USER_INFO=user_info
    LOGGING_LEVEL=INFO
    MODE="daily" # 'daily' or 'backload'
    BACKLOAD_START_DATE=YYYY-MM-DD
    BACKLOAD_END_DATE=YYYY-MM-DD
    UPDATE_INTERVAL_HOURS=6

## Usage
The script can be run in two modes: daily and backload.

## Daily Mode
This mode processes data for the last 24 hours, divided into specified intervals.

    ```bash
    python main.py

    ```
Set the following environment variables:

    ```bash
    MODE=daily
    UPDATE_INTERVAL_HOURS=6 (or your preferred interval)
    ```

## Backload Mode
This mode processes historical data for a specified date range.

    ```bash
    python main.py

    ```
Set the following environment variables:

    ```bash
    MODE=backload
    BACKLOAD_START_DATE=2023-01-01
    BACKLOAD_END_DATE=2023-12-31
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


## Deployment
This script is designed to be deployed on Google Cloud Run. Set the environment variables in your Cloud Run configuration.

