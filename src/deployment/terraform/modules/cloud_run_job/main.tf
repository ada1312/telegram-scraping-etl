resource "google_cloud_run_v2_job" "default" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        resources {
          limits = {
            cpu    = "4"
            memory = "8Gi"
          }
        }
        image = var.container_image        
        env {
          name = "LOOGING_LEVEL"
          value = var.logging_level
        }
        env {
          name = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name = "DATASET_ID"
          value = var.dataset_id
        }
        env {
          name = "TABLE_ID_BVOL"
          value = var.table_id_bvol
        }
        env {
          name = "TABLE_ID"
          value = var.table_id_options
        }
        env {
          name = "UNDERLYINGASSET"
          value = var.underlying_asset
        }
        env {
          name = "UNDERLYINGASSET_USDT"
          value = var.underlying_asset_price
        }
        env {
          name = "URL"
          value = var.url
        }
        env {
          name = "PROXY_URL"
          value = var.proxy_url
        }
        env {
          name = "RATE_LIMIT_BATCH_SIZE"
          value = var.rate_limit_batch_size
        }

      }
      service_account   = var.service_account_email
      timeout           = var.job_timeout
      vpc_access {
        connector       = "projects/${var.project_id}/locations/${var.location}/connectors/binance-vpc-connector"
        egress          = "ALL_TRAFFIC"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage, 
    ]
  }
}

resource "google_cloud_scheduler_job" "job" {
  name                  = var.scheduler_job_name
  schedule              = var.scheduler_schedule
  time_zone             = var.time_zone
  region                = var.location
  http_target {
    uri                 = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    http_method         = "POST"

    oauth_token {
      service_account_email = var.service_account_email
    }    
  }
  depends_on = [google_cloud_run_v2_job.default]
}