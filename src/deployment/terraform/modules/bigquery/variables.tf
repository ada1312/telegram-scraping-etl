variable "dataset_id" {
  description = "The BigQuery dataset ID."
  type        = string
}

variable "location" {
  description = "The location for the BigQuery dataset."
  type        = string
}

variable "table_id_options" {
  description = "The ID of the options table"
  type        = string
}

variable "table_id_bvol" {
  description = "The ID of the bvol table"
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