variable "project_id" {
  type = string
}

variable "api_id" {
  type = string
}

variable "api_hash" {
  type = string
}

variable "phone_number" {
  type = string
}

variable "telegram_session_string" {
  type      = string
  sensitive = true
}
