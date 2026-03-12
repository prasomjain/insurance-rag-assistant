import requests
import json

try:
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "Show me denied claims for diabetes"}
    )
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
