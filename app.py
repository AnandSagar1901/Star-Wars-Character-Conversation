import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import random
import io
import base64
import threading
import os
from google import genai

API_KEY = " Put your Gemini API Key here " 
client = genai.Client(api_key=API_KEY)

# --- Helpers ---
def fetch_character(num):
    url = f"https://swapi.dev/api/people/{num}/"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def generate_character_image(character_name, style="cartoon", size="64x64"):
    try:
        response = client.images.generate(
            prompt=f"{character_name} from Star Wars, {style} style",
            size=size
        )
        image_bytes = response.data[0].b64_json
        img_data = io.BytesIO(base64.b64decode(image_bytes))
        pil_image = Image.open(img_data)
        return pil_image
    except Exception:
        pil_image = Image.new("RGB", (64,64), "#333")
        return pil_image

def get_cached_image(character_name, style="cartoon"):
    safe_name = character_name.replace(" ", "_")
    filename = f"images/{safe_name}_{style}.png"
    if os.path.exists(filename):
        return ImageTk.PhotoImage(Image.open(filename))
    else:
        img = generate_character_image(character_name, style)
        img.save(filename)
        return ImageTk.PhotoImage(img)

def placeholder_image():
    img = Image.new("RGB", (64, 64), "#333")
    return ImageTk.PhotoImage(img)

def generate_conversation(question, characters, length="medium"):
    if len(characters) == 1:
        char = characters[0]
        prompt = f"You are {char['name']} from Star Wars. Answer ONLY as them. Question: {question}. Response length: {length}."
    elif len(characters) == 2:
        c1, c2 = characters
        prompt = f"Simulate a dialogue between {c1['name']} and {c2['name']}. Alternate lines, prefix with names. Question: {question}. Response length: {length}."
    else:
        c1, c2, c3 = characters
        prompt = f"Simulate a dialogue between {c1['name']}, {c2['name']}, and {c3['name']}. Alternate lines, prefix with names. Question: {question}. Response length: {length}."

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    text = response.candidates[0].content.parts[0].text
    return text.replace("As an AI", "").strip()

# --- GUI Styling ---
root = tk.Tk()
root.title("Star Wars Chat App")
root.configure(bg="#0c0c0c")

FONT_MAIN = ("Jetbrains Mono", 11)
FONT_BOLD = ("Jetbrains Mono", 11, "bold")

BG_MAIN = "#0c0c0c"
BG_FRAME = "#1a1a1a"
FG_TEXT = "#ffffff"
FG_HIGHLIGHT = "#ffe81f"
BTN_BG = "#222222"
BTN_FG = "#ffe81f"
ENTRY_BG = "#222222"
ENTRY_FG = "#ffffff"

style = ttk.Style()
style.theme_use('default')
style.configure("TLabelframe", background=BG_FRAME, foreground=FG_TEXT)
style.configure("TLabelframe.Label", background=BG_FRAME, foreground=FG_TEXT)
style.configure("TLabel", background=BG_FRAME, foreground=FG_TEXT, font=FONT_MAIN)
style.configure("TButton", background=BTN_BG, foreground=BTN_FG, font=FONT_MAIN)
style.map("TButton", background=[('active', '#444')])

characters = []
character_images = []
img_labels = []

# --- Character Selection Frame ---
frame_select = ttk.LabelFrame(root, text="Character Selection")
frame_select.pack(pady=10, padx=10, fill=tk.X)

tk.Label(frame_select, text="Number of characters (1-3):", bg=BG_FRAME, fg=FG_TEXT, font=FONT_MAIN).grid(row=0, column=0, sticky="w")
num_chars_var = tk.StringVar(value="1")
num_chars_entry = ttk.Combobox(frame_select, textvariable=num_chars_var, width=5)
num_chars_entry['values'] = ("1","2","3")
num_chars_entry.grid(row=0, column=1, sticky="w")

tk.Label(frame_select, text="Art style:", bg=BG_FRAME, fg=FG_TEXT, font=FONT_MAIN).grid(row=1, column=0, sticky="w")
style_var = tk.StringVar(value="cartoon")
style_menu = ttk.Combobox(frame_select, textvariable=style_var, width=10)
style_menu['values'] = ("cartoon","anime","realistic","pixel")
style_menu.grid(row=1, column=1, sticky="w")

char_entries = []
for i in range(3):
    tk.Label(frame_select, text=f"Character {i+1} ID (1-88, N=random):", bg=BG_FRAME, fg=FG_TEXT, font=FONT_MAIN).grid(row=2+i, column=0, sticky="w")
    entry = tk.Entry(frame_select, width=12, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_TEXT, font=FONT_MAIN)
    entry.grid(row=2+i, column=1, sticky="w", pady=2)
    char_entries.append(entry)

tk.Label(frame_select, text="Response length:", bg=BG_FRAME, fg=FG_TEXT, font=FONT_MAIN).grid(row=5, column=0, sticky="w")
length_var = tk.StringVar(value="medium")
length_menu = ttk.Combobox(frame_select, textvariable=length_var, width=10)
length_menu['values'] = ("short","medium","long")
length_menu.grid(row=5, column=1, sticky="w")

# --- Chat Frame ---
frame_chat = tk.Frame(root, bg=BG_MAIN)
frame_chat.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

canvas_chat = tk.Canvas(frame_chat, bg=BG_MAIN, highlightthickness=0)
scrollbar = tk.Scrollbar(frame_chat, orient="vertical", command=canvas_chat.yview)
scrollable_frame = tk.Frame(canvas_chat, bg=BG_MAIN)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas_chat.configure(scrollregion=canvas_chat.bbox("all"))
)
canvas_chat.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas_chat.configure(yscrollcommand=scrollbar.set)
canvas_chat.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- Input Frame ---
input_frame = tk.Frame(root, bg=BG_MAIN)
input_frame.pack(pady=5, fill=tk.X)

entry_question = tk.Entry(input_frame, width=60, font=FONT_MAIN, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_TEXT)
entry_question.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
send_btn = tk.Button(input_frame, text="Send", bg=BTN_BG, fg=BTN_FG, font=FONT_MAIN, activebackground="#444")
send_btn.pack(side=tk.LEFT, padx=5)
entry_question.bind("<Return>", lambda event: send_question())

# --- Functions ---
def generate_images_async():
    global character_images
    for idx, char in enumerate(characters):
        if char['name'] == "You": continue
        img = get_cached_image(char['name'], style_var.get())
        character_images[idx] = img

def start_chat():
    global characters, character_images, img_labels
    characters = []
    character_images = []

    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    img_labels.clear()

    num_chars = int(num_chars_var.get())

    for i in range(num_chars):
        if i == 2:
            characters.append({"name":"You","height":"?","mass":"?","birth_year":"?"})
            character_images.append(placeholder_image())
            continue
        val = char_entries[i].get()
        num = random.randint(1,88) if val.lower()=="n" else int(val)
        char = fetch_character(num)
        if char:
            characters.append(char)
            character_images.append(placeholder_image())
        else:
            messagebox.showerror("Error", f"Invalid character ID: {val}")
            return

    lbl = tk.Label(scrollable_frame, text="Chat started! Images loading...", fg=FG_TEXT, bg=BG_MAIN, font=FONT_MAIN)
    lbl.pack(anchor="w")

    threading.Thread(target=generate_images_async, daemon=True).start()

def send_question():
    question = entry_question.get()
    if not question: return
    entry_question.delete(0, tk.END)

    answer = generate_conversation(question, characters, length_var.get())

    # Display question
    q_label = tk.Label(scrollable_frame, text=f"> {question}", fg=FG_HIGHLIGHT, bg=BG_MAIN, font=FONT_BOLD)
    q_label.pack(anchor="w", pady=2)

    # Display answer with images inline
    for idx, line in enumerate(answer.split("\n")):
        line_strip = line.strip()
        if not line_strip: continue
        char_idx = 0
        if characters[0]['name'] in line_strip:
            char_idx = 0
        elif len(characters)>1 and characters[1]['name'] in line_strip:
            char_idx = 1
        elif len(characters)>2 and characters[2]['name'] in line_strip:
            char_idx = 2

        frame_line = tk.Frame(scrollable_frame, bg=BG_MAIN)
        frame_line.pack(anchor="w", pady=2)
        lbl_img = tk.Label(frame_line, image=character_images[char_idx], borderwidth=2, relief="ridge")
        lbl_img.pack(side="left", padx=2)
        lbl_text = tk.Label(frame_line, text=line_strip, fg=FG_TEXT, bg=BG_MAIN, font=FONT_MAIN)
        lbl_text.pack(side="left", padx=5)

# --- Buttons ---
start_btn = tk.Button(frame_select, text="Start Chat", bg=BTN_BG, fg=BTN_FG, font=FONT_MAIN, command=start_chat)
start_btn.grid(row=6, columnspan=2, pady=10)
send_btn.config(command=send_question)

# Ensure images folder exists
if not os.path.exists("images"):
    os.mkdir("images")

root.mainloop()
