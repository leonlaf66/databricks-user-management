locals {
  databricks_account_id = "fdb4196f-c790-47b0-8e7f-0fde5097dbd5"
}

module "databricks_management" {
  source = "../common_modules/databricks_management"

  group_users = {
    "data-scientists" = [
      {
        user_name    = "eyang@dbxdemo.com",
        display_name = "Elta Yang"
      },
      {
        user_name    = "eli@dbxdemo.com",
        display_name = "Ella Li"
      }
    ],
    "data-engineers" = [
      {
        user_name    = "eyang@dbxdemo.com",
        display_name = "Elta Yang"
      }
    ]
  }

  group_permissions = {
    "data-scientists" = true
    "data-engineers"  = false
  }
}
