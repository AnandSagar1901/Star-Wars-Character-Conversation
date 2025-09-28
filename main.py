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

def conversation(client, question):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=(
            f"You are {character['name']} from Star Wars. "
            f"Speak in their tone. Here are your details: "
            f"Height: {character['height']}, Mass: {character['mass']}, "
            f"Birth Year: {character['birth_year']}. "
            f"Take in the following question: {question} and respond in character."
        )
    )
    return response.text


while True:
    question = input("Ask your question (or type 'Y' to quit): ")
    if question.upper() == "Y":
        break

    answer = conversation(client, question)
    print(f"{character['name']}: {answer}")
