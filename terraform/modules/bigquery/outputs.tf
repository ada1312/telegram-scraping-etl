output "table_chat_config" {
  value = google_bigquery_table.chat_config.table_id
}

output "table_chat_history" {
  value = google_bigquery_table.chat_history.table_id
}

output "table_chat_info" {
  value = google_bigquery_table.chat_info.table_id
}

output "table_user_info" {
  value = google_bigquery_table.user_info.table_id
}

output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}