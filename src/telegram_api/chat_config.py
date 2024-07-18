from google.cloud import bigquery

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
            bigquery.ScalarQueryParameter("chat_id", "STRING", chat_id),
            bigquery.ScalarQueryParameter("username", "STRING", username),
            bigquery.ArrayQueryParameter("dates", "DATE", dates),
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
    
    return [dict(row) for row in results]


async def update_processed_date(bq_client, dataset_id, table_chat_config, chat_id, processed_date):
    query = f"""
    UPDATE `{dataset_id}.{table_chat_config}`
    SET last_processed_date = @processed_date
    WHERE id = @chat_id
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("processed_date", "DATE", processed_date),
            bigquery.ScalarQueryParameter("chat_id", "STRING", chat_id),
        ]
    )
    
    query_job = bq_client.query(query, job_config=job_config)
    await query_job.result()
