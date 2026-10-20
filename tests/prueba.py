import requests

url = "https://readyapi.net/api/v1/search/query"
headers = {"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"}
payload = {"query": "I need to travel far away quickly", "top_k": 2}

response = requests.post(url, json=payload, headers=headers)
print(response.json())




