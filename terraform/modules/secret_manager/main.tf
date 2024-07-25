resource "google_secret_manager_secret" "secret" {
  secret_id = var.secret_id
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_version" {
  secret      = google_secret_manager_secret.secret.id
  secret_data = var.secret_value
}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}

resource "google_secret_manager_secret" "telegram_session_string" {
  secret_id = "telegram-session-string"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "telegram_session_string" {
  secret = google_secret_manager_secret.telegram_session_string.id
  secret_data = var.telegram_session_string
}