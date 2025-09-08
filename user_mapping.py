import requests
import json
import argparse # Added for command-line arguments

def get_oauth_token(account_id, client_id, client_secret):
    """
    Obtains an OAuth token from the Databricks Account API.
    """
    token_url = f"https://accounts.cloud.databricks.com/oidc/accounts/{account_id}/v1/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'scope': 'all-apis'
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data, auth=(client_id, client_secret))
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.HTTPError as err:
        print(f"Error getting OAuth token: {err}")
        print(f"Response Body: {err.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        return None

def get_all_paginated_data(url, headers):
    """
    Fetches all items from a paginated Databricks API endpoint.
    """
    all_items = []
    start_index = 1
    
    while True:
        paginated_url = f"{url}?startIndex={start_index}"
        try:
            response = requests.get(paginated_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('Resources', [])
            if not items:
                break
                
            all_items.extend(items)
            
            total_results = data.get('totalResults', 0)
            items_per_page = data.get('itemsPerPage', len(items))
            
            if (start_index - 1 + items_per_page) >= total_results:
                break
                
            start_index += items_per_page

        except requests.exceptions.HTTPError as err:
            print(f"❌ Error fetching data from {paginated_url}: {err}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"❌ A network error occurred while fetching from {paginated_url}: {e}")
            return []
            
    return all_items

def main():
    """
    Main function to fetch users, groups, and map their relationships.
    """
    # --- Setup Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(description="Fetch Databricks users and their group mappings.")
    parser.add_argument("--account-id", required=True, help="Your Databricks Account ID.")
    parser.add_argument("--client-id", required=True, help="The Service Principal Client ID.")
    parser.add_argument("--client-secret", required=True, help="The Service Principal Client Secret.")
    args = parser.parse_args()

    print("\n🔄 Authenticating and fetching data...")

    # 1. Get OAuth Token using command-line args
    access_token = get_oauth_token(args.account_id, args.client_id, args.client_secret)
    if not access_token:
        return

    # 2. Prepare API Headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    api_base_url = f"https://accounts.cloud.databricks.com/api/2.0/accounts/{args.account_id}/scim/v2"

    # 3. Fetch all users and groups
    print("Fetching users...")
    users_url = f"{api_base_url}/Users"
    all_users = get_all_paginated_data(users_url, headers)
    
    print("Fetching groups...")
    groups_url = f"{api_base_url}/Groups"
    all_groups = get_all_paginated_data(groups_url, headers)

    if not all_users:
        print("No users found or an error occurred.")
        return

    # 4. Create a user mapping and process groups
    user_map = {user['id']: {
        "userName": user.get('userName', 'N/A'),
        "displayName": user.get('displayName', 'N/A'),
        "groups": []
    } for user in all_users}
    
    print("Mapping users to groups...")
    for group in all_groups:
        group_name = group.get('displayName', 'Unknown Group')
        members = group.get('members', [])
        for member in members:
            user_id = member.get('value')
            if user_id in user_map:
                user_map[user_id]['groups'].append(group_name)

    # 5. Output the results
    output_data = list(user_map.values())
    print(json.dumps(output_data, indent=4))
    output_filename = "databricks_user_group_mapping.json"
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"\n✅ Success! Data has been written to '{output_filename}'")
    print(f"Processed {len(all_users)} users and {len(all_groups)} groups.")

if __name__ == "__main__":
    main()