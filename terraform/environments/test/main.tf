provider "google" {
  project = var.project_id
  region  = "us-central1"
}

module "service_account" {
  source             = "../../modules/service_account"
  account_id         = "telegram-chat-etl-agent"
  display_name       = "telegram-chat-etl-agent"
  description        = "Service account with cloud run permissions and read/write access to telegram dataset in container-testing-381309"
  project_id         = var.project_id

  role_id            = "telegram_chat_etl_agent"
  role_title         = "telegram chat etl agent"
  role_description   = "Custom role for telegram etl agent permissions"
  role_permissions   = [
    "bigquery.jobs.create",
    "run.jobs.run",
    "run.executions.cancel",
    "run.routes.invoke",
    "bigquery.tables.get",
    "bigquery.tables.getData",
    "bigquery.datasets.get"
  ]
}

module "bigquery" {
  source                      = "../../modules/bigquery"
  dataset_id                  = "telegram"
  location                    = "us-central1"
  table_chat_config           = "chat_config"
  table_chat_history          = "chat_history"
  table_chat_info             = "chat_info"
  table_user_info             = "user_info"
  dataset_description         = "Telegram chat data" 
  labels                      = {
    env = "test"
  }
  service_account_email       = module.service_account.service_account_email
}

module "secret_manager" {
  source                     = "../../modules/secret_manager"
  project_id                 = var.project_id
  secret_id                  = {
    api_id       = "api_id"
    api_hash     = "api_hash"
    phone_number = "phone"
  }
  secret_value = {
    api_id       = var.api_id
    api_hash     = var.api_hash
    phone_number = var.phone_number
  }
  service_account_email = module.service_account.service_account_email
  telegram_session_string = var.telegram_session_string
}

module "cloud_run" {
  source                        = "../../modules/cloud_run_job"
  location                      = "us-central1"
  project_id                    = var.project_id
  service_account_email         = module.service_account.service_account_email
  container_image               = "gcr.io/container-testing-381309/telegram_update_etl:latest"
  job_name                      = "telegram-chat-etl"
  scheduler_job_name            = "telegram-chat-etl"
  scheduler_schedule            = "0 1 * * *"
  job_timeout                   = "3540s"

  api_id_secret                 = module.secret_manager.secret_ids["api_id"]
  api_hash_secret               = module.secret_manager.secret_ids["api_hash"]
  phone_number_secret           = module.secret_manager.secret_ids["phone_number"]
  chat_usernames                = "pythontelegrambotgroup,binanceexchange,lobsters_chat"
  sample_size                   = 1000
  logging_level                 = "INFO"
  dataset_id                    = module.bigquery.dataset_id
  chat_config                   = module.bigquery.table_chat_config
  chat_history                  = module.bigquery.table_chat_history
  chat_info                     = module.bigquery.table_chat_info
  user_info                     = module.bigquery.table_user_info
  mode                          = "day_ago" # backload or day_ago or recent
  backload_start_date           = "2024-07-13"
  backload_end_date             = "2024-07-23"
  telegram_session_string       = var.telegram_session_string
}

output "service_account_email" {
  value = module.service_account.service_account_email
}

output "service_account_unique_id" {
  value = module.service_account.service_account_unique_id
}

output "custom_role_id" {
  value = module.service_account.custom_role_id
}

output "chat_config_table_id" {
  value = module.bigquery.table_chat_config
}

output "chat_history_table_id" {
  value = module.bigquery.table_chat_history
}

output "chat_info_table_id" {
  value = module.bigquery.table_chat_info
}

output "user_info_table_id" {
  value = module.bigquery.table_user_info
}
