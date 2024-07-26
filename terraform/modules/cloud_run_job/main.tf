resource "google_cloud_run_v2_job" "default" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        image = var.container_image
        
        dynamic "env" {
          for_each = {
            CHAT_USERNAMES= var.chat_usernames
            SAMPLE_SIZE= var.sample_size
            LOGGING_LEVEL= var.logging_level
            PROJECT_ID =  var.project_id
            DATASET_ID= var.dataset_id
            TABLE_CHAT_CONFIG= var.chat_config
            TABLE_CHAT_HISTORY= var.chat_history
            TABLE_CHAT_INFO= var.chat_info
            TABLE_USER_INFO= var.user_info
            MODE= var.mode 
            BACKLOAD_START_DATE= var.backload_start_date
            BACKLOAD_END_DATE= var.backload_end_date
            TELEGRAM_SESSION_STRING= var.telegram_session_string

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


resource "google_cloud_scheduler_job" "job" {
  name     = var.scheduler_job_name
  schedule = var.scheduler_schedule
  time_zone = var.time_zone
  region = var.location
  http_target {
    uri        = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    http_method = "POST"

    oauth_token {
      service_account_email = var.service_account_email
    }    
  }
  depends_on = [google_cloud_run_v2_job.default]
}