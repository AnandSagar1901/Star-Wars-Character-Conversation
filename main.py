import requests
import random
from google import genai

API_KEY = "AIzaSyDnH8K6JObrOJOFcQqwgMb6KHX5N5hi1P8"
client = genai.Client(api_key=API_KEY)

# Get a list of people
response = requests.get("https://swapi.dev/api/people/")
data = response.json()

num = random.randint(1,88)

desired_character = input("Which character ID would you like to be? (1-88)For Character IDs please refer to README (If you want random please enter: N): ")

if desired_character != "N" and desired_character != "n":
    num = int(desired_character)
elif desired_character == "N" or desired_character == "n":
    num = random.randint(1,88)

character_url = f"https://swapi.dev/api/people/{num}/"
response = requests.get(character_url)


if response.status_code == 200:
    character = response.json()
    print("Fetching character...")
    print("Character Fetched!")
    print(f"You got {character['name']}  ")
else:
    print("That character ID doesn’t exist, rerun.")



length = input("How long should the responses to be? (short, medium, long)(Please enter in all lower case): ")

def conversation(client, question, length):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=(
            f"You are {character['name']} from Star Wars. "
            f"Speak in their tone. Here are your details: "
            f"Height: {character['height']}, Mass: {character['mass']}, "
            f"Birth Year: {character['birth_year']}. "
            f"Take in the following question: {question} and respond in character."
            f"Also take into consideration that your responses should be {length}."
        )
    )
    return response.text


while True:
    question = input("Ask your question (or type 'Y' to quit): ")
    if question == "Y":
        break

    answer = conversation(client, question, length)
    print(f"{character['name']} says: {answer}")
