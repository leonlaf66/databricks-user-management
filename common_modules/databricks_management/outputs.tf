output "group_ids" {
  description = "The IDs of the created Databricks groups."
  value       = { for group in databricks_group.groups : group.display_name => group.id }
}

output "user_ids" {
  description = "The IDs of the created Databricks users."
  value       = { for user in databricks_user.users : user.user_name => user.id }
}