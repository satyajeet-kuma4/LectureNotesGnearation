from flask import Flask, request, jsonify
import yt_dlp
import os
import ffmpeg
import whisper
import google.generativeai as genai
from textwrap import wrap

import key

app = Flask(__name__)

# === CONFIG ===

output_dir = 'temp_audio'
os.makedirs(output_dir, exist_ok=True)

genai.configure(api_key=key.GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")
model_whisper = whisper.load_model("base")

# === Utility Functions ===
def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title', 'audio')
        ext = info_dict.get('ext', 'm4a')
        return os.path.join(output_dir, f"{title}.{ext}")

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

def generate_notes_from_chunk(chunk, chunk_number):
    prompt = generate_notes_prompt(chunk, chunk_number)
    return model.generate_content(prompt).text.strip()

def generate_questions_from_notes(notes, chunk_number):
    prompt = generate_questions_prompt(notes, chunk_number)
    return model.generate_content(prompt).text.strip()


@app.route('/process', methods=['POST'])
def process_youtube_url():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    audio_path = None
    wav_audio_path = None

    try:
        # Download and convert audio
        audio_path = download_youtube_audio(url)
        wav_audio_path = convert_to_wav(audio_path)

        # Transcribe audio
        result = model_whisper.transcribe(wav_audio_path)
        transcript = result['text']
        chunks = split_text_into_chunks(transcript)

        all_notes = []
        all_questions = []

        # Process each chunk
        for i, chunk in enumerate(chunks, 1):
            notes = generate_notes_from_chunk(chunk, i)
            questions = generate_questions_from_notes(notes, i)
            all_notes.append(notes)
            all_questions.append(questions)

        return jsonify({
            'notes': all_notes,
            'questions': all_questions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        #   Cleanup
        for path in [audio_path, wav_audio_path]:
            if path and os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    app.run(debug=True)
