resource "google_bigquery_table" "chat_config" {
  dataset_id           = var.dataset_id
  table_id             = var.table_chat_config
  labels               = var.labels
  schema               = file("${path.module}/chat_config.json")
  deletion_protection  = false
}

resource "google_bigquery_table" "chat_history" {
  dataset_id           = var.dataset_id
  table_id             = var.table_chat_history    
  labels               = var.labels
  schema               = file("${path.module}/chat_history.json")
  deletion_protection  = false
}

resource "google_bigquery_table" "chat_info" {
  dataset_id           = var.dataset_id
  table_id             = var.table_chat_info
  labels               = var.labels
  schema               = file("${path.module}/chat_info.json")
  deletion_protection  = false
}

resource "google_bigquery_table" "user_info" {
  dataset_id           = var.dataset_id
  table_id             = var.table_user_info
  labels               = var.labels
  schema               = file("${path.module}/user_info.json")
  deletion_protection  = false
}

resource "google_bigquery_dataset_iam_member" "dataset_writer" {
  dataset_id           = var.dataset_id
  role                 = "roles/bigquery.dataEditor"
  member               = "serviceAccount:${var.service_account_email}"
}