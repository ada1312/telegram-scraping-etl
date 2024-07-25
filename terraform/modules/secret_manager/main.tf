resource "google_secret_manager_secret" "secrets" {
  for_each = { for key, value in var.secret_id : key => value }

  project   = var.project_id
  secret_id = each.value

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_versions" {
  for_each    = google_secret_manager_secret.secrets
  secret      = each.value.secret_id
  secret_data = var.secret_value[each.key]
}
