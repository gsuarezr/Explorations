import requests
import random
import argparse
# TODO: This is printing the wrong collection, I should Also refactor this to 
# nested collections
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
    # Define custom weights for specific collections by name
    custom_weights = {
        'mythesis': 5,        # Giving "mythesis" a weight of 5
        'Quantum AI': 3       # Giving "Quantum AI" a weight of 3
    }
    
    # Assign weights
    weighted_collections = []
    for collection in collections:
        collection_name = collection['data']['name']  # Get the name of the collection
        # Assign higher weights to specified collections by name
        weight = custom_weights.get(collection_name, 1)  # Default weight is 1
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
        # If no collection_id, fetch unfiled items
        url = UNFILED_ITEMS_URL
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching collection items: {response.status_code}")
        return []

# Print item details including authors and the collection it came from
def print_item_details(item, collection_name):
    title = item['data'].get('title', 'No title')
    item_id = item['key']

    # Fetch author information if available
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Select N random Zotero items from different collections.")
    parser.add_argument('-N', type=int, default=1, help='Number of items to select (default is 1)')
    args = parser.parse_args()

    # Fetch collections and unfiled items
    collections = fetch_collections()
    unfiled_items = fetch_unfiled_items()

    if not collections and not unfiled_items:
        return

    # Treat unfiled items as a special "collection"
    if unfiled_items:
        unfiled_collection = {
            'data': {'name': 'Unfiled Items'},
            'key': None,  # Use None to indicate unfiled items
            'items': unfiled_items
        }
        collections.append(unfiled_collection)

    weighted_collections = assign_weights(collections)

    # Randomly select N collections
    chosen_collections = choose_weighted_collections(weighted_collections, args.N)

    selected_items = []
    
    for collection in chosen_collections:
        # Fetch items from the chosen collection
        if collection['key']:  # If a regular collection
            items = fetch_collection_items(collection['key'])
        else:  # If "Unfiled Items"
            items = unfiled_items
        
        if items:
            selected_items.append((random.choice(items), collection['data']['name']))  # Randomly choose one item from the collection
    
    # Print details for all selected items
    for item, collection_name in selected_items:
        print_item_details(item, collection_name)

if __name__ == "__main__":
    main()
