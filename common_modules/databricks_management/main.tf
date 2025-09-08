locals {
  all_memberships = flatten([
    for group_name, users in var.group_users : [
      for user in users : {
        user_name          = user.user_name
        display_name       = user.display_name
        group_display_name = group_name
      }
    ]
  ])

  unique_users = merge(flatten([
    for group, users in var.group_users : [
      for user in users : {
        (user.user_name) = {
          display_name = user.display_name
        }
      }
    ]
  ])...)
}



resource "databricks_group" "groups" {
  for_each = toset(keys(var.group_users))

  display_name               = each.key
  allow_cluster_create       = lookup(var.group_permissions, each.key, false)
  allow_instance_pool_create = lookup(var.group_permissions, each.key, false)
}

resource "databricks_user" "users" {
  for_each = local.unique_users

  user_name    = each.key
  display_name = each.value.display_name
}

resource "databricks_group_member" "group_members" {
  for_each = { for membership in local.all_memberships : "${membership.group_display_name}-${membership.user_name}" => membership }

  group_id  = databricks_group.groups[each.value.group_display_name].id
  member_id = databricks_user.users[each.value.user_name].id
}