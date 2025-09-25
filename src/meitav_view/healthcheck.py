import sys

import requests

url = "http://localhost:8080/health"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raises an exception if response status code is not in the 2xx range
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1)
else:
    print("Request successful!")
    sys.exit(0)
