variable "project_id" {
  description = "The GCP project ID."
  type        = string
}
variable "telegram_phone_number" {
  type        = string
  sensitive   = true
  description = "Telegram phone number"
}

variable "telegram_api_id" {
  type        = string
  sensitive   = true
  description = "Telegram API ID"
}

variable "telegram_api_hash" {
  type        = string
  sensitive   = true
  description = "Telegram API hash"
}

variable "telegram_session_string" {
  type        = string
  sensitive   = true
  description = "Telegram session string"
}