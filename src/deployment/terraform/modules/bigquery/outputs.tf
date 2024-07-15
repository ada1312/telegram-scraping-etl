output "chat_config" {
  description = "The ID of the table created for chat configuration data."
  value       = google_bigquery_table.chat_config.table_id
}

output "chat_history" {
  description = "The ID of the table created for chat history data."
  value       = google_bigquery_table.chat_history.table_id
} 

output "chat_info" {
  description = "The ID of the table created for chat info data."
  value       = google_bigquery_table.chat_info.table_id
}

output "user_info" {
  description = "The ID of the table created for user info data."
  value       = google_bigquery_table.user_info.table_id
}