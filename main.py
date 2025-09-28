import requests
import random
from google import genai

API_KEY = "AIzaSyDnH8K6JObrOJOFcQqwgMb6KHX5N5hi1P8"
client = genai.Client(api_key=API_KEY)

# Get a list of people
response = requests.get("https://swapi.dev/api/people/")
data = response.json()

num = random.randint(1,88)

character_url = f"https://swapi.dev/api/people/{num}/"
response = requests.get(character_url)

if response.status_code == 200:
    character = response.json()
    print("You got:", character["name"])
else:
    print("That character ID doesn’t exist, rerun.")


print(character["name"])

def conversation(client):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Answer my questions and talk as if you are " + character["name"],
    )
    return response.text