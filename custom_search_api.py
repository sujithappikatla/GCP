import requests

def get_search_results(query, api_key="AIzaSyBqsPAjwFYgXz2FBQ3eKy7Tt419bcUe3io", cx="57a93014e41594929", num=10):
    # Construct the URL
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num
    }

    try:
        # Send GET request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse JSON response
        results = response.json()
        
        # Extract URLs from items
        urls = []
        if "items" in results:
            urls = [item["link"] for item in results["items"]]
        
        return urls

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing response: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    urls = get_search_results("photosynthesis")
    print("\nSearch Result URLs:")
    url_list = ""
    for url in urls:
        url_list += url + "\n"
    print(url_list)

