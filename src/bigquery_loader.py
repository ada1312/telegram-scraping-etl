import logging
from google.cloud.bigquery import LoadJobConfig, SourceFormat 
from google.api_core.exceptions import BadRequest, GoogleAPIError
import json
from io import StringIO

async def upload_to_bigquery(client, data, table_type, dataset_id, table_chat_config, table_chat_history, table_chat_info, table_user_info):
    logging.info(f"Starting upload to BigQuery for table type: {table_type}")
    
    # Basic data validation
    if not data:
        logging.error("No data to upload")
        return
    if not isinstance(data, list):
        logging.error("Data must be a list")
        return
    if not all(isinstance(item, dict) for item in data):
        logging.error("All items in data must be dictionaries")
        return
    
    table_id_mapping = {
        'chat_config': table_chat_config,
        'chat_history': table_chat_history,
        'chat_info': table_chat_info,
        'user_info': table_user_info,
    }

    table_id = table_id_mapping.get(table_type)
    if not table_id:
        logging.error(f"Invalid table type: {table_type}")
        return

    json_data = [json.dumps(obj) for obj in data]
    newline_delimited_data = "\n".join(json_data)

    logging.info(f"Uploading {len(data)} rows to BigQuery table: {table_id}")
    try:
        table_ref = client.dataset(dataset_id).table(table_id)
        job_config = LoadJobConfig()
        job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True

        data_file = StringIO(newline_delimited_data)

        logging.info(f"Sample data (first item): {json.dumps(data[0], indent=2)}")

        job = client.load_table_from_file(
            data_file,
            table_ref,
            location='us-central1',
            job_config=job_config,
        )

        job.result()  # Wait for the job to complete

        logging.info(f"Data uploaded to BigQuery table {table_id} successfully. Job ID: {job.job_id}")

    except BadRequest as e:
        logging.error(f"Bad request error: {e}")
        logging.error(f"Error details: {e.errors}")
    except GoogleAPIError as e:
        logging.error(f"Error connecting to BigQuery: {e}")
    except ValueError as e:
        logging.error(f"Invalid JSON data: {e}")
    except Exception as e:
        logging.error(f"Error occurred when uploading data to BigQuery: {e}")
        logging.error(f"Error type: {type(e)}")