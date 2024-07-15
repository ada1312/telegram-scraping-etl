variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "location" {
  description = "The location for the BigQuery dataset."
  type        = string
}

variable "table_chat_config" {
  description = "The BigQuery table name for chat configuration data."
  type        = string
}

variable "table_chat_history" {
  description = "The BigQuery table name for chat history data."
  type        = string
}

variable "table_chat_info" {
  description = "The BigQuery table name for chat info data."
  type        = string
}

variable "table_user_info" {
  description = "The BigQuery table name for user info data."
  type        = string 
}

variable "labels" {
  description = "A map of labels to assign to the tables created by this module."
  type        = map(string)
}

variable "service_account_email" {
  description = "The email address of the service account to use for authentication."
  type        = string
}

variable "schema_path" {
  description = "The path to the schema file for the BigQuery table"
  type        = string
}