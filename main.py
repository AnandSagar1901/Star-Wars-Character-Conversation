import requests
import random
from google import genai

API_KEY = " Put your Gemini API Key here " 
client = genai.Client(api_key=API_KEY)

def fetch_character(num):
    """Fetch a character by ID from SWAPI"""
    character_url = f"https://swapi.dev/api/people/{num}/"
    response = requests.get(character_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# --- Character Selection ---
mode = input("Do you want 1, 2, or 3 characters? (Enter 1, 2, or 3): ")

characters = []
for i in range(int(mode)):
    if i == 2:  # Third slot → user themself
        print("Adding YOU as a third character...")
        characters.append({"name": "You", "height": "?", "mass": "?", "birth_year": "?"})
        continue

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

# --- Conversation function ---
def conversation(client, question, length, characters):
    if len(characters) == 1:
        char = characters[0]
        prompt = (
            f"You are {char['name']} from Star Wars. "
            f"Answer ONLY as {char['name']}, no extra notes. "
            f"Question: {question}. Response length: {length}. "
            "(short = 1-2 sentences, medium = 3-4, long = 5+)."
        )
    elif len(characters) == 2:
        c1, c2 = characters
        prompt = (
            f"Simulate a dialogue between {c1['name']} and {c2['name']}. "
            f"Alternate lines, prefix each with their name. "
            f"Answer ONLY as them, no extra notes. "
            f"Question: {question}. Response length: {length}."
        )
    else:  # 3 characters (two from SWAPI + You)
        c1, c2, c3 = characters
        prompt = (
            f"Simulate a dialogue between {c1['name']}, {c2['name']}, and {c3['name']}. "
            f"Alternate lines, prefix each with their name. "
            f"Answer ONLY as them, no extra notes. "
            f"Question: {question}. Response length: {length}."
        )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    text = response.candidates[0].content.parts[0].text

    # Remove possible AI meta responses
    clean_text = text.replace("As an AI", "").replace("I'm an AI", "").strip()
    return clean_text

# --- Chat Loop ---
while True:
    question = input("Ask your question (or type 'Y' to quit): ")
    if question.lower() == "y":
        break

    answer = conversation(client, question, length, characters)
    print(answer)
