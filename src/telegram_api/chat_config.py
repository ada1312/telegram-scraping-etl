from google.cloud import bigquery
from datetime import date
import asyncio

async def upsert_chat_config(bq_client, dataset_id, table_chat_config, chat_id, username, dates):
    query = f"""
    MERGE `{dataset_id}.{table_chat_config}` AS target
    USING (SELECT @chat_id AS id, @username AS username) AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET dates_to_load = ARRAY_CONCAT(target.dates_to_load, @dates)
    WHEN NOT MATCHED THEN
        INSERT (id, username, dates_to_load)
        VALUES (@chat_id, @username, @dates)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("chat_id", "STRING", str(chat_id)),
            bigquery.ScalarQueryParameter("username", "STRING", username or ''),
            bigquery.ArrayQueryParameter("dates", "DATE", [d if isinstance(d, date) else date.fromisoformat(d) for d in dates]),
        ]
    )

    query_job = bq_client.query(query, job_config=job_config)
    await query_job.result()

async def get_chat_configs(bq_client, dataset_id, table_chat_config):
    query = f"""
    SELECT id, username, dates_to_load
    FROM `{dataset_id}.{table_chat_config}`
    """
    
    query_job = bq_client.query(query)
    results = query_job.result()
    
    chat_configs = {}
    for row in results:
        config = dict(row)
        config['id'] = str(config['id'])
        config['username'] = config['username'] or ''
        config['dates_to_load'] = config['dates_to_load'] or [date.today()]  # Use today's date if empty
        chat_configs[config['username']] = config
        
    return chat_configs

async def update_processed_date(bq_client, dataset_id, table_chat_config, chat_id, new_dates):
    query = f"""
    UPDATE `{dataset_id}.{table_chat_config}`
    SET dates_to_load = ARRAY(
        SELECT DISTINCT date
        FROM UNNEST(ARRAY_CONCAT(dates_to_load, @new_dates)) AS date
    )
    WHERE id = @chat_id
    """
    
    new_dates_str = [d.isoformat() if isinstance(d, date) else d for d in new_dates]
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("new_dates", "DATE", new_dates_str),
            bigquery.ScalarQueryParameter("chat_id", "STRING", str(chat_id)),
        ]
    )
    
    def run_query():
        query_job = bq_client.query(query, job_config=job_config)
        query_job.result()
        return query_job

    return await asyncio.to_thread(run_query)

def ensure_chat_config_exists(bq_client, dataset_id, table_chat_config, chat_id, username):
    today = date.today().isoformat()
    query = f"""
    MERGE `{dataset_id}.{table_chat_config}` AS target
    USING (SELECT @chat_id AS id, @username AS username) AS source
    ON target.id = source.id
    WHEN NOT MATCHED THEN
        INSERT (id, username, dates_to_load)
        VALUES (@chat_id, @username, [])
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("chat_id", "STRING", str(chat_id)),
            bigquery.ScalarQueryParameter("username", "STRING", username or ''),
            bigquery.ScalarQueryParameter("today", "DATE", today),
        ]
    )
    
    query_job = bq_client.query(query, job_config=job_config)
    query_job.result()