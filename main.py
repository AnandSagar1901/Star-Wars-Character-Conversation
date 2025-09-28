import requests
import random
from google import genai

API_KEY = "AIzaSyDnH8K6JObrOJOFcQqwgMb6KHX5N5hi1P8" 
client = genai.Client(api_key=API_KEY)

# --- Helper function to fetch characters ---
def fetch_character(num):
    character_url = f"https://swapi.dev/api/people/{num}/"
    response = requests.get(character_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# --- Character Selection ---
mode = input("Do you want 1 character or 2 characters? (Enter 1 or 2): ")

characters = []
for i in range(int(mode)):
    desired_character = input(
        f"Which character ID would you like for character {i+1}? (1-88). "
        "Enter N for random: "
    )

    if desired_character.lower() == "n":
        num = random.randint(1, 88)
    else:
        num = int(desired_character)

    character = fetch_character(num)
    if character:
        print(f"Fetching character {i+1}...")
        print("Character Fetched!")
        print(f"You got {character['name']}")
        characters.append(character)
    else:
        print("That character ID doesn’t exist, rerun.")
        exit()

length = input("How long should the responses be? (short, medium, long): ")

# --- Conversation function (supports 1 or 2 characters) ---
def conversation(client, question, length):
    if len(characters) == 1:
        character = characters[0]
        prompt = (
            f"You are {character['name']} from Star Wars. "
            f"Speak in their tone. Here are your details: "
            f"Height: {character['height']}, Mass: {character['mass']}, "
            f"Birth Year: {character['birth_year']}. "
            f"Take in the following question: {question} and respond in character. "
            f"Also take into consideration that your responses should be {length}. "
            "(Short: 1-2 sentences, Medium: 3-4 sentences, Long: 5+ sentences)"
        )
    else:
        char1, char2 = characters
        prompt = (
            f"Simulate a conversation between {char1['name']} and {char2['name']} "
            f"from Star Wars. Alternate lines, prefixing with their names. "
            f"Use their tone, knowledge, and mannerisms. Here are their details:\n"
            f"- {char1['name']}: Height {char1['height']}, Mass {char1['mass']}, Birth Year {char1['birth_year']}\n"
            f"- {char2['name']}: Height {char2['height']}, Mass {char2['mass']}, Birth Year {char2['birth_year']}\n"
            f"Take in the following question: {question} and respond as a dialogue. "
            f"Responses should be {length}. "
            "(Short: 1-2 sentences, Medium: 3-4, Long: 5+)."
        )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.candidates[0].content.parts[0].text

# --- Chat Loop ---
while True:
    question = input("Ask your question (or type 'Y' to quit): ")
    if question.lower() == "y":
        break

    answer = conversation(client, question, length)
    print(answer)
