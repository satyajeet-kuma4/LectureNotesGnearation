import yt_dlp
import os
import ffmpeg
import whisper
import google.generativeai as genai
from textwrap import wrap

# === CONFIGURATION ===
GOOGLE_API_KEY = "AIzaSyB8e3Tr7yFdEQXrJiTZuydDL03QYnty8bE"
output_dir = r'C:\Users\Satyajeet kumar\Desktop\Lecture_transcripts_genration'
os.makedirs(output_dir, exist_ok=True)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# === FUNCTIONS ===

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'audio')
        ext = info_dict.get('ext', 'm4a')
        audio_path = os.path.join(output_dir, f"{title}.{ext}")
    return audio_path

def convert_to_wav(audio_path):
    wav_path = os.path.splitext(audio_path)[0] + '.wav'
    ffmpeg.input(audio_path).output(wav_path, ac=1, ar='16000').run(overwrite_output=True)
    return wav_path

def split_text_into_chunks(text, max_chars=6000):
    return wrap(text, max_chars)

def generate_notes_prompt(chunk, chunk_number):
    return f"""
You are an expert assistant that generates detailed and structured lecture notes from transcript chunks.

Transcript Chunk:
{chunk}

Generate notes in the following format:

---

### 📘 Notes for Chunk {chunk_number}

#### 🗂️ Key Concepts & Topics:
- [Summarized key points here]

#### 🧠 Key Takeaways:
- [Important takeaways or conclusions]

#### 💬 Important Quotes or Examples:
- [Relevant examples or quotes if applicable]

#### 📌 Definitions / Terminology:
- [Term]: [Explanation, if any]

#### ✅ Action Items or Follow-up:
- [Actionable points, reading suggestions, or exercises]

---

Please output only the structured notes in the exact format above.
"""

def generate_questions_prompt(notes, chunk_number):
    return f"""
You are a helpful assistant. Based on the structured lecture notes below, generate a list of 5 thoughtful and relevant questions that a student might be asked after studying these notes.

Lecture Notes (Chunk {chunk_number}):
{notes}

Format the output as:

---

### ❓ Questions for Chunk {chunk_number}
1. ...
2. ...
3. ...
4. ...
5. ...

---
"""

def generate_questions_from_notes(notes, chunk_number):
    prompt = generate_questions_prompt(notes, chunk_number)
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_notes_from_chunk(chunk, chunk_number):
    prompt = generate_notes_prompt(chunk, chunk_number)
    response = model.generate_content(prompt)
    return response.text.strip()

# === MAIN PIPELINE ===
url = "https://youtu.be/QVKj3LADCnA?si=hIzrf53xzpDLHUYT"
audio_path = download_youtube_audio(url)
wav_audio_path = convert_to_wav(audio_path)

model_whisper = whisper.load_model("base")
result = model_whisper.transcribe(wav_audio_path)
transcript = result["text"]

chunks = split_text_into_chunks(transcript)
notes_file = os.path.join(output_dir, "lecture_notes_structured.txt")
questions_file = os.path.join(output_dir, "lecture_questions.txt")

with open(notes_file, "w", encoding="utf-8") as nf, open(questions_file, "w", encoding="utf-8") as qf:
    for i, chunk in enumerate(chunks, 1):
        print(f"🔹 Processing chunk {i} of {len(chunks)}...")
        notes = generate_notes_from_chunk(chunk, i)
        questions = generate_questions_from_notes(notes, i)
        nf.write(notes + "\n\n")
        qf.write(questions + "\n\n")

print(f"\n✅ Notes saved to: {notes_file}")
print(f"✅ Questions saved to: {questions_file}")
