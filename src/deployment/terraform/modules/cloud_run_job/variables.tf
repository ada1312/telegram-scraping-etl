variable "job_name" {
  description = "The name of the Cloud Run job"
  type        = string
}

variable "location" {
  description = "The location where the job and scheduler will be deployed"
  type        = string
}

variable "container_image" {
  description = "The container image for the Cloud Run job"
  type        = string
}

variable "service_account_email" {
  description = "The service account email to use with the Cloud Run job"
  type        = string
}

variable "job_timeout" {
  description = "The maximum duration of the Cloud Run job"
  default     = "3540s"
  type        = string
}

variable "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  type        = string
}

variable "scheduler_schedule" {
  description = "The schedule on which the Cloud Scheduler job should run"
  type        = string
}

variable "time_zone" {
  description = "The time zone for the Cloud Scheduler job schedule"
  type        = string
  default     = "Etc/UTC"
}

variable "logging_level" {
  description = "The logging level for the Cloud Run job"
  type        = string
  default     = "INFO"
}

variable "project_id" {
  description = "The project ID"
  type        = string
}
variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}
variable "chat_config" {
  description = "The configuration for the chat loading"
  type        = string
}

variable "chat_history" {
  description = "Table for all chat history"
  type        = string
}

variable "chat_info" {
  description = "Table for all chat info"
  type        = string
}

variable "user_info" {
  description = "Table for all user info"
  type        = string
}

variable "api_id_secret" {
  type = string
  description = "The full resource name of the API ID secret"
}

variable "api_hash_secret" {
  type = string
  description = "The full resource name of the API hash secret"
}

variable "phone_number_secret" {
  type = string
  description = "The full resource name of the phone number secret"
}

variable "chat_username" {
  description = "Chat username for which to load the chat history"
  type        = string
}

variable "sample_size" {
  description = "Sample size for the chat history, None for all"
  type        = string
}
