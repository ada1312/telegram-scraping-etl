import logging
import json
from io import StringIO
from google.cloud.bigquery import LoadJobConfig, SourceFormat, Client
import asyncio
from config import load_config

client = Client(project=load_config().project_id)

async def async_load(data, table_id) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        load,
        data,
        table_id
    )

def load(data, table_id) -> bool:
    try:
        if data is not None:
            logging.debug(f"uploading {len(data)} rows to {table_id}")
            jsonl_data = '\n'.join(json.dumps(item) for item in data)
            table_ref = client.dataset(load_config().dataset_id).table(table_id)
            job_config = LoadJobConfig() 
            job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON            
            
            with StringIO(jsonl_data) as json_data_io:
                job = client.load_table_from_file(
                    json_data_io,
                    table_ref,
                    location='us-central1',
                    job_config=job_config,
                )
            
            result = job.result()
            if result.state == 'DONE' and result.error_result is None:
                logging.info(f"successfully uploaded data to {table_id}")
                return True
            else:
                logging.error(f"failed to upload data to {table_id}")
                if result.error_result:
                    logging.error(f"{table_id} upload result: {job.error_result}")
                if result.errors:
                    for error in result.errors:
                        logging.error(f"{table_id} upload error: {error}")
                return False
        else:
            logging.error(f"no data to upload to {table_id}")
            return False

    except Exception as e:
        logging.error(f"error uploading data to {table_id}: {e}")
        return False