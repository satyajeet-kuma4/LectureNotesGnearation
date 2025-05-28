import json
import yt_dlp
import os
import ffmpeg
import whisper
import cv2
import pytesseract
import re
from datetime import timedelta

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Paths
output_dir = r'C:\Users\Satyajeet kumar\Desktop\Lecture_transcripts_genration'
os.makedirs(output_dir, exist_ok=True)

# Download video from YouTube
def download_youtube_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_dir}/video.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': False,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return os.path.join(output_dir, 'video.mp4')

# Extract audio from video as WAV
def extract_audio(video_path):
    audio_path = os.path.splitext(video_path)[0] + '.wav'
    ffmpeg.input(video_path).output(audio_path, ac=1, ar='16000').run(overwrite_output=True)
    return audio_path

# Transcribe audio with timestamps
def transcribe_with_timestamps(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, verbose=False, word_timestamps=False)
    transcript_segments = [(seg['start'], seg['end'], seg['text']) for seg in result['segments']]
    return transcript_segments

# Preprocessing to improve OCR accuracy
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)  # Apply thresholding
    processed_frame = cv2.medianBlur(thresh, 3)  # Optional: Remove noise using median filter
    return processed_frame

# Clean the OCR text by removing unwanted characters
def clean_ocr_text(text):
    cleaned_text = re.sub(r'[^A-Za-z0-9\s.,!?-]', '', text)  # Remove unwanted characters
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove extra spaces
    return cleaned_text

# Run OCR on frames with preprocessing and cleaning
def ocr_on_frames(frames):
    ocr_results = []
    for timestamp, frame in frames:
        processed_frame = preprocess_frame(frame)
        custom_config = r'--oem 3 --psm 6'  # Best for structured text
        text = pytesseract.image_to_string(processed_frame, config=custom_config)
        cleaned_text = clean_ocr_text(text)  # Clean OCR output
        ocr_results.append((timestamp, cleaned_text))
    return ocr_results

# Extract video frames with larger time window (e.g., 30 sec interval)
def extract_frames(video_path, timestamps, interval=30):
    cap = cv2.VideoCapture(video_path)
    frames = []
    for start, end, _ in timestamps:
        midpoint = (start + end) / 2
        adjusted_midpoint = max(midpoint - interval / 2, 0)  # Ensure we don't go below 0
        cap.set(cv2.CAP_PROP_POS_MSEC, adjusted_midpoint * 1000)  # Set to new midpoint
        success, frame = cap.read()
        if success:
            frames.append((adjusted_midpoint, frame))
    cap.release()
    return frames

# Main pipeline
def process_lecture_video(youtube_url):
    video_path = download_youtube_video(youtube_url)
    audio_path = extract_audio(video_path)
    transcript_segments = transcribe_with_timestamps(audio_path)
    
    # Extract frames with 30-second time window
    frames = extract_frames(video_path, transcript_segments, interval=30)
    
    ocr_results = ocr_on_frames(frames)

    combined = []
    for (start, end, text), (timestamp, ocr_text) in zip(transcript_segments, ocr_results):
        combined.append({
            'timestamp': str(timedelta(seconds=int(timestamp))),
            'transcript': text,
            'ocr': ocr_text
        })

    # Save to JSON file
    json_path = os.path.join(output_dir, 'lecture_output.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=4)

    return combined

# Example usage
youtube_url = "https://youtu.be/QVKj3LADCnA?si=hIzrf53xzpDLHUYT"


# Generate prompt
data = process_lecture_video(youtube_url)
transcript_text = "\n".join([entry['transcript'] for entry in data])
ocr_slide_text = "\n".join([entry['ocr'] for entry in data])

prompt = f"""
You are a note-taking assistant.

Below is the spoken transcript of a lecture, along with slide text captured via OCR.

Your task is to generate **concise, clean, and structured lecture notes**.

🧠 Important Instructions:
- Use the **same examples, equations, and variable names** mentioned in the transcript and slides.
- Summarize in clear points or sections.
- Highlight key concepts, important steps (like methods or derivations), and final results.
- If possible, organize steps of problem-solving or algorithms.
- Keep the tone educational and student-friendly.

Transcript:
{transcript_text}

Slides (OCR):
{ocr_slide_text}
"""

# Stream response from OpenAI
from openai import OpenAI

client = OpenAI(api_key="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")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that creates lecture notes."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    stream=True
)

notes = ""
for chunk in response:
    if chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
        notes += content
