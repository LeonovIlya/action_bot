import requests

response = requests.get("https://calendar.kuzyak.in/api/calendar/2025")
print(response.json())