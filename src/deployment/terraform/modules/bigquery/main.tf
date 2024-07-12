resource "google_bigquery_table" "options" {
  dataset_id           = var.dataset_id
  table_id             = var.table_id_options
  labels               = var.labels
  schema               = file("${path.module}/options.json")
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  deletion_protection  = false
}

resource "google_bigquery_table" "bvol" {
  dataset_id           = var.dataset_id
  table_id             = var.table_id_bvol    
  labels               = var.labels
  schema               = file("${path.module}/bvol.json")
    time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  deletion_protection  = false
}

resource "google_bigquery_dataset_iam_member" "dataset_writer" {
  dataset_id           = var.dataset_id
  role                 = "roles/bigquery.dataEditor"
  member               = "serviceAccount:${var.service_account_email}"
}