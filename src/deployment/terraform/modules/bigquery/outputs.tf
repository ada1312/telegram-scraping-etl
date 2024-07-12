output "table_id_options" {
  description = "The ID of the table created for options data."
  value       = google_bigquery_table.options.table_id
}

output "table_id_bvol" {
  description = "The ID of the table created for bvol data."
  value       = google_bigquery_table.bvol.table_id
}