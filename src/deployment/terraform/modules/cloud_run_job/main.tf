resource "google_cloud_run_v2_job" "default" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        image = var.container_image
        
        dynamic "env" {
          for_each = {
            LOGGING_LEVEL         = var.logging_level
            PROJECT_ID            = var.project_id
            DATASET_ID            = var.dataset_id
            CHAT_CONFIG           = var.chat_config
            CHAT_HISTORY          = var.chat_history
            CHAT_INFO             = var.chat_info
            USER_INFO             = var.user_info
            CHAT_USERNAME         = var.chat_username
            SAMPLE_SIZE           = var.sample_size
          }
          content {
            name  = env.key
            value = env.value
          }
        }

        # Add secret environment variables
        env {
          name = "API_ID"
          value_source {
            secret_key_ref {
              secret  = var.api_id_secret
              version = "latest"
            }
          }
        }
        env {
          name = "API_HASH"
          value_source {
            secret_key_ref {
              secret  = var.api_hash_secret
              version = "latest"
            }
          }
        }
        env {
          name = "PHONE_NUMBER"
          value_source {
            secret_key_ref {
              secret  = var.phone_number_secret
              version = "latest"
            }
          }
        }
      }
      service_account = var.service_account_email
      timeout         = var.job_timeout
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
}