output "table_chat_config" {
  value = google_bigquery_table.chat_config.id
}

output "table_chat_history" {
  value = google_bigquery_table.chat_history.id
}

output "table_chat_info" {
  value = google_bigquery_table.chat_info.id
}

output "table_user_info" {
  value = google_bigquery_table.user_info.id
}
