variable "group_users" {
  description = "A map where keys are group display names and values are lists of user objects, each with a user_name (email) and display_name."
  type = map(list(object({
    user_name    = string
    display_name = string
  })))
  default = {}
}

variable "group_permissions" {
  description = "A map where keys are group display names and values are booleans indicating if the group should have cluster create permissions."
  type        = map(bool)
  default = {
    "data-scientists" = true
    "data-engineers"  = false
  }
}