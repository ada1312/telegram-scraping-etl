output "table_chat_config_id" {
  value = google_bigquery_table.chat_config.id
  description = "The ID of the BigQuery table for chat configuration data."
}

output "table_chat_history_id" {
  value = google_bigquery_table.chat_history.id
  description = "The ID of the BigQuery table for chat history data."
}

output "table_chat_info_id" {
  value = google_bigquery_table.chat_info.id
  description = "The ID of the BigQuery table for chat info data."
}

output "table_user_info_id" {
  value = google_bigquery_table.user_info.id
  description = "The ID of the BigQuery table for user info data."
}