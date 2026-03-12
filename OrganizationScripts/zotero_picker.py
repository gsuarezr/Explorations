import requests
import random
import argparse

# Replace with your actual user ID and API key
USER_ID = '8218749'
API_KEY = 'sLg4qjuiLEhTkE11c2R4s8Fy'

# Zotero API endpoints
COLLECTIONS_URL = f"https://api.zotero.org/users/{USER_ID}/collections"
UNFILED_ITEMS_URL = f"https://api.zotero.org/users/{USER_ID}/items/top?collection=&tag=&limit=100"

# Fetch collections from Zotero
def fetch_collections():
    headers = {
        'Zotero-API-Key': API_KEY
    }
    response = requests.get(COLLECTIONS_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching collections: {response.status_code}")
        return []

# Fetch unfiled items from Zotero
def fetch_unfiled_items():
    headers = {
        'Zotero-API-Key': API_KEY
    }
    response = requests.get(UNFILED_ITEMS_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching unfiled items: {response.status_code}")
        return []

# Assign weights to collections (including unfiled items as a collection)
def assign_weights(collections):
    custom_weights = {
        'mythesis': 5,
        'Quantum AI': 3
    }
    
    weighted_collections = []
    for collection in collections:
        collection_name = collection['data']['name']
        weight = custom_weights.get(collection_name, 1)
        weighted_collections.append((collection, weight))
    
    return weighted_collections

# Select N collections based on weights
def choose_weighted_collections(weighted_collections, N):
    collections, weights = zip(*weighted_collections)
    chosen_collections = random.choices(collections, weights=weights, k=N)
    return chosen_collections

# Fetch items from a specific collection
def fetch_collection_items(collection_id=None):
    headers = {
        'Zotero-API-Key': API_KEY
    }
    if collection_id:
        url = f"https://api.zotero.org/users/{USER_ID}/items/top?collection={collection_id}"
    else:
        url = UNFILED_ITEMS_URL

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        items = response.json()
        if collection_id:
            # Filter items to only include those in the given collection
            filtered_items = [item for item in items if collection_id in item['data'].get('collections', [])]
        else:
            filtered_items = items

        return filtered_items
    else:
        print(f"Error fetching collection items: {response.status_code}")
        return []

# Print item details including authors and the collection it came from
def print_item_details(item, collection_name):
    title = item['data'].get('title', 'No title')
    item_id = item['key']
    creators = item['data'].get('creators', [])
    authors = ', '.join([f"{creator['lastName']}, {creator.get('firstName', '')}" for creator in creators if creator['creatorType'] == 'author'])
    
    print("%%%%%%%%%%%%%%")
    print(f"Collection: {collection_name}")
    print(f"Title: {title}")
    if authors:
        print(f"Author(s): {authors}")
    else:
        print("Author(s): Not available")
    print(f"Item ID: {item_id}")
    print("%%%%%%%%%%%%%%")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Select N random Zotero items from different collections.")
    parser.add_argument('-N', type=int, default=1, help='Number of items to select (default is 1)')
    args = parser.parse_args()

    collections = fetch_collections()
    unfiled_items = fetch_unfiled_items()

    if not collections and not unfiled_items:
        return

    if unfiled_items:
        unfiled_collection = {
            'data': {'name': 'Unfiled Items'},
            'key': None,
            'items': unfiled_items
        }
        collections.append(unfiled_collection)

    weighted_collections = assign_weights(collections)
    selected_items = []
    used_items = set()  # Track already selected items

    # Loop until we've selected the desired number of items
    while len(selected_items) < args.N:
        chosen_collections = choose_weighted_collections(weighted_collections, args.N)

        for collection in chosen_collections:
            if len(selected_items) >= args.N:
                break

            if collection['key']:
                items = fetch_collection_items(collection['key'])
            else:
                items = unfiled_items

            if items:
                available_items = [item for item in items if item['key'] not in used_items]  # Avoid duplicates
                if available_items:
                    chosen_item = random.choice(available_items)
                    selected_items.append((chosen_item, collection['data']['name']))
                    used_items.add(chosen_item['key'])  # Mark item as used

    # Print the details of the selected items
    for item, collection_name in selected_items[:args.N]:
        print_item_details(item, collection_name)

if __name__ == "__main__":
    main()


# import requests
# import random
# import argparse
# # TODO: This is printing the wrong collection, I should Also refactor this to 
# # nested collections
# # Replace with your actual user ID and API key
# USER_ID = '8218749'
# API_KEY = 'sLg4qjuiLEhTkE11c2R4s8Fy'

# # Zotero API endpoints
# COLLECTIONS_URL = f"https://api.zotero.org/users/{USER_ID}/collections"
# UNFILED_ITEMS_URL = f"https://api.zotero.org/users/{USER_ID}/items/top?collection=&tag=&limit=100"

# # Fetch collections from Zotero
# def fetch_collections():
#     headers = {
#         'Zotero-API-Key': API_KEY
#     }
#     response = requests.get(COLLECTIONS_URL, headers=headers)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching collections: {response.status_code}")
#         return []

# # Fetch unfiled items from Zotero
# def fetch_unfiled_items():
#     headers = {
#         'Zotero-API-Key': API_KEY
#     }
#     response = requests.get(UNFILED_ITEMS_URL, headers=headers)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching unfiled items: {response.status_code}")
#         return []

# # Assign weights to collections (including unfiled items as a collection)
# def assign_weights(collections):
#     # Define custom weights for specific collections by name
#     custom_weights = {
#         'mythesis': 5,        # Giving "mythesis" a weight of 5
#         'Quantum AI': 3       # Giving "Quantum AI" a weight of 3
#     }
    
#     # Assign weights
#     weighted_collections = []
#     for collection in collections:
#         collection_name = collection['data']['name']  # Get the name of the collection
#         # Assign higher weights to specified collections by name
#         weight = custom_weights.get(collection_name, 1)  # Default weight is 1
#         weighted_collections.append((collection, weight))
    
#     return weighted_collections

# # Select N collections based on weights
# def choose_weighted_collections(weighted_collections, N):
#     collections, weights = zip(*weighted_collections)
#     chosen_collections = random.choices(collections, weights=weights, k=N)
#     return chosen_collections

# # Fetch items from a specific collection
# def fetch_collection_items(collection_id=None):
#     headers = {
#         'Zotero-API-Key': API_KEY
#     }
#     if collection_id:
#         url = f"https://api.zotero.org/users/{USER_ID}/items/top?collection={collection_id}"
#     else:
#         # If no collection_id, fetch unfiled items
#         url = UNFILED_ITEMS_URL
    
#     response = requests.get(url, headers=headers)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching collection items: {response.status_code}")
#         return []

# # Print item details including authors and the collection it came from
# def print_item_details(item, collection_name):
#     title = item['data'].get('title', 'No title')
#     item_id = item['key']

#     # Fetch author information if available
#     creators = item['data'].get('creators', [])
#     authors = ', '.join([f"{creator['lastName']}, {creator.get('firstName', '')}" for creator in creators if creator['creatorType'] == 'author'])
    
#     print("%%%%%%%%%%%%%%")
#     print(f"Collection: {collection_name}")
#     print(f"Title: {title}")
#     if authors:
#         print(f"Author(s): {authors}")
#     else:
#         print("Author(s): Not available")
#     print(f"Item ID: {item_id}")
#     print("%%%%%%%%%%%%%%")



# # Main function
# def main():
#     # Parse command-line arguments
#     parser = argparse.ArgumentParser(description="Select N random Zotero items from different collections.")
#     parser.add_argument('-N', type=int, default=1, help='Number of items to select (default is 1)')
#     args = parser.parse_args()

#     # Fetch collections and unfiled items
#     collections = fetch_collections()
#     unfiled_items = fetch_unfiled_items()

#     if not collections and not unfiled_items:
#         return

#     # Treat unfiled items as a special "collection"
#     if unfiled_items:
#         unfiled_collection = {
#             'data': {'name': 'Unfiled Items'},
#             'key': None,  # Use None to indicate unfiled items
#             'items': unfiled_items
#         }
#         collections.append(unfiled_collection)

#     weighted_collections = assign_weights(collections)

#     # Randomly select N collections
#     chosen_collections = choose_weighted_collections(weighted_collections, args.N)

#     selected_items = []
    
#     for collection in chosen_collections:
#         # Fetch items from the chosen collection
#         if collection['key']:  # If a regular collection
#             items = fetch_collection_items(collection['key'])
#         else:  # If "Unfiled Items"
#             items = unfiled_items
        
#         if items:
#             print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#             print("Collection",collection)
#             print("%%%%%%%%%%%%%%%%%%%%%%%%%%")
#             selected_items.append((random.choice(items), collection['data']['name']))  # Randomly choose one item from the collection
    
#     # Print details for all selected items
#     for item, collection_name in selected_items:
#         print_item_details(item, collection_name)

# if __name__ == "__main__":
#     main()

# import requests
# import random
# import argparse
# import json
# from pprint import pprint

# # Replace with your actual user ID and API key
# USER_ID = '8218749'
# API_KEY = 'sLg4qjuiLEhTkE11c2R4s8Fy'

# # Zotero API endpoints
# COLLECTIONS_URL = f"https://api.zotero.org/users/{USER_ID}/collections"
# ITEMS_URL = f"https://api.zotero.org/users/{USER_ID}/items"

# def fetch_data(url):
#     headers = {'Zotero-API-Key': API_KEY}
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data: {response.status_code}")
#         return []

# def fetch_collections():
#     return fetch_data(COLLECTIONS_URL)

# def fetch_items():
#     return fetch_data(ITEMS_URL)

# def build_collection_tree(collections):
#     collection_dict = {coll['key']: coll for coll in collections}
#     root_collections = []

#     for coll in collections:
#         parent_key = coll['data'].get('parentCollection')
#         if parent_key:
#             parent = collection_dict.get(parent_key)
#             if parent:
#                 parent.setdefault('children', []).append(coll)
#         else:
#             root_collections.append(coll)

#     return root_collections

# def assign_weights(collections):
#     custom_weights = {'mythesis': 5, 'Quantum AI': 3}
    
#     def assign_weight_recursive(collection):
#         collection_name = collection['data']['name']
#         weight = custom_weights.get(collection_name, 1)
#         weighted_collection = (collection, weight)
        
#         if 'children' in collection:
#             children = [assign_weight_recursive(child) for child in collection['children']]
#             return (weighted_collection, children)
#         else:
#             return weighted_collection

#     return [assign_weight_recursive(coll) for coll in collections]

# def flatten_collections(weighted_collections):
#     def flatten(collection_tree):
#         if isinstance(collection_tree, tuple) and len(collection_tree) == 2:
#             coll, weight = collection_tree
#             if isinstance(weight, (int, float)):
#                 yield (coll, weight)
#             if isinstance(coll, dict) and 'children' in coll:
#                 for child in coll.get('children', []):
#                     yield from flatten((child, weight))
#         elif isinstance(collection_tree, list):
#             for item in collection_tree:
#                 yield from flatten(item)

#     return list(flatten(weighted_collections))

# def choose_weighted_collections(flat_collections, N):
#     if not flat_collections:
#         print("No collections found after flattening.")
#         return []

#     collections, weights = zip(*flat_collections)
#     return random.choices(collections, weights=weights, k=min(N, len(collections)))

# def get_collection_path(collection, collection_dict):
#     path = [collection['data']['name']]
#     parent_key = collection['data'].get('parentCollection')
#     while parent_key:
#         parent = collection_dict.get(parent_key)
#         if parent:
#             path.append(parent['data']['name'])
#             parent_key = parent['data'].get('parentCollection')
#         else:
#             break
#     return ' > '.join(reversed(path))

# def print_item_details(item, collection_path):
#     title = item['data'].get('title', 'No title')
#     item_id = item['key']
#     creators = item['data'].get('creators', [])
#     authors = ', '.join([f"{creator.get('lastName', '')}, {creator.get('firstName', '')}" for creator in creators if creator.get('creatorType') == 'author'])
    
#     print("%%%%%%%%%%%%%%")
#     print(f"Collection: {collection_path}")
#     print(f"Title: {title}")
#     if authors:
#         print(f"Author(s): {authors}")
#     else:
#         print("Author(s): Not available")
#     print(f"Item ID: {item_id}")
#     print("%%%%%%%%%%%%%%")

# def main():
#     parser = argparse.ArgumentParser(description="Select N random Zotero items from different collections.")
#     parser.add_argument('-N', type=int, default=1, help='Number of items to select (default is 1)')
#     args = parser.parse_args()

#     collections = fetch_collections()
#     items = fetch_items()

#     if not collections:
#         print("No collections found.")
#         return

#     if not items:
#         print("No items found.")
#         return

#     print(f"Number of collections: {len(collections)}")
#     print(f"Number of items: {len(items)}")

#     collection_dict = {coll['key']: coll for coll in collections}
#     root_collections = build_collection_tree(collections)

#     weighted_collections = assign_weights(root_collections)
    
#     print("\nWeighted collections structure:")
#     pprint(weighted_collections, depth=3)
    
#     flat_collections = flatten_collections(weighted_collections)
    
#     print("\nFlattened collections:")
#     for i, (coll, weight) in enumerate(flat_collections):
#         print(f"{i}: {coll['data']['name']} (weight: {weight})")

#     chosen_collections = choose_weighted_collections(flat_collections, args.N)
    
#     print(f"\nNumber of chosen collections: {len(chosen_collections)}")
#     print("\nChosen collections:")
#     for i, coll in enumerate(chosen_collections):
#         print(f"{i + 1}: {coll['data']['name']}")

#     selected_items = []
#     for collection in chosen_collections:
#         collection_items = [item for item in items if collection['key'] in item['data'].get('collections', [])]
#         if collection_items:
#             selected_items.append((random.choice(collection_items), collection))

#     for item, collection in selected_items:
#         collection_path = get_collection_path(collection, collection_dict)
#         print_item_details(item, collection_path)

# if __name__ == "__main__":
#     main()