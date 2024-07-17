resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = var.dataset_id
  description                 = "Dataset for Telegram chat data"
  location                    = var.location
  default_table_expiration_ms = null
  labels                      = var.labels

  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "chat_config" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.table_chat_config
  schema              = file("${var.schema_path}/chat_config.json")
  deletion_protection = false

  depends_on = [google_bigquery_dataset.dataset]
}

resource "google_bigquery_table" "chat_history" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.table_chat_history
  schema              = file("${var.schema_path}/chat_history.json")
  deletion_protection = false

  depends_on = [google_bigquery_dataset.dataset]
}

resource "google_bigquery_table" "chat_info" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.table_chat_info
  schema              = file("${var.schema_path}/chat_info.json")
  deletion_protection = false

  depends_on = [google_bigquery_dataset.dataset]
}

resource "google_bigquery_table" "user_info" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.table_user_info
  schema              = file("${var.schema_path}/user_info.json")
  deletion_protection = false

  depends_on = [google_bigquery_dataset.dataset]
}

resource "google_bigquery_dataset_iam_member" "dataset_writer" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${var.service_account_email}"

  depends_on = [google_bigquery_dataset.dataset]
}