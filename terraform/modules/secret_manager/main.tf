resource "google_secret_manager_secret" "api_id" {
  project     = var.project_id
  secret_id   = "api_id"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "api_id_version" {
  secret       = google_secret_manager_secret.api_id.id
  secret_data  = var.secret_value["api_id"]
}

resource "google_secret_manager_secret" "api_hash" {
  project     = var.project_id
  secret_id   = "api_hash"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "api_hash_version" {
  secret       = google_secret_manager_secret.api_hash.id
  secret_data  = var.secret_value["api_hash"]
}

resource "google_secret_manager_secret" "phone_number" {
  project     = var.project_id
  secret_id   = "phone_number"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "phone_number_version" {
  secret       = google_secret_manager_secret.phone_number.id
  secret_data  = var.secret_value["phone_number"]
}
