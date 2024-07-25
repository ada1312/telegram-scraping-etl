output "secret_ids" {
  value = {
    api_id       = google_secret_manager_secret.api_id.id
    api_hash     = google_secret_manager_secret.api_hash.id
    phone_number = google_secret_manager_secret.phone_number.id
  }
}
