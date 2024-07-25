variable "project_id" {
  type = string
}

variable "secret_id" {
  type = map(string)
}

variable "secret_value" {
  type      = map(string)
  sensitive = true
}

variable "service_account_email" {
  type = string
}

variable "telegram_session_string" {
  type      = string
  sensitive = true
}
