import streamlit as st
import os
import requests
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

# Load .env
load_dotenv()

# Load API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Check for API keys
if not GEMINI_API_KEY or not YOUTUBE_API_KEY:
    st.error("⚠️ Missing API keys in .env file!")
    st.stop()

# Functions
def call_gemini_flash(prompt):
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    params = {"key": GEMINI_API_KEY}

    response = requests.post(endpoint, headers=headers, json=body, params=params)

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        st.error(f"❌ Gemini API Error: {response.status_code}")
        return None

def get_youtube_videos(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "maxResults": 5,
        "type": "video"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        videos = []
        for item in response.json()["items"]:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            videos.append((title, f"https://www.youtube.com/watch?v={video_id}"))
        return videos
    else:
        st.error(f"❌ YouTube API Error: {response.status_code}")
        return []

# UI Setup
st.set_page_config(page_title="Educational Content Generator", page_icon="📚")
st.title("📚 Educational Content Generator")

# Sidebar task selector
task = st.sidebar.radio("Select a Task", [
    "Summarize Content",
    "Generate Quiz",
    "Create Flashcards",
    "Generate Audio Summary",
    "Suggest YouTube Videos"
])

# Main content input section
st.subheader("✍️ Enter or Upload Your Educational Content")

# Always show input area
text_input = st.text_area("Paste your content here 👇", height=200)

uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])

content = text_input  # prioritize text area

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")

# Proceed only if content is available
if content.strip() != "":
    if task == "Summarize Content":
        st.subheader("🧠 Summary")
        with st.spinner("Generating summary..."):
            result = call_gemini_flash(f"Summarize this educational content:\n{content}")
            if result:
                st.write(result)

    elif task == "Generate Quiz":
        st.subheader("📝 Quiz")
        with st.spinner("Generating quiz..."):
            prompt = f"Generate 5 multiple-choice questions with 4 options each and the correct answer labeled based on:\n{content}"
            result = call_gemini_flash(prompt)
            if result:
                st.markdown(result)

    elif task == "Create Flashcards":
        st.subheader("📇 Flashcards")
        with st.spinner("Generating flashcards..."):
            prompt = f"Create 10 flashcards in the format: Term - Definition:\n{content}"
            result = call_gemini_flash(prompt)
            if result:
                st.markdown(result)

    elif task == "Generate Audio Summary":
        st.subheader("🔊 Audio Summary")
        with st.spinner("Generating audio..."):
            prompt = f"Give a 1-minute spoken summary of this content:\n{content}"
            text = call_gemini_flash(prompt)
            if text:
                tts = gTTS(text)
                audio_fp = BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3')
                st.markdown("📝 Text Summary:")
                st.write(text)

    elif task == "Suggest YouTube Videos":
        st.subheader("🎥 YouTube Video Suggestions")
        with st.spinner("Searching YouTube..."):
            query = f"educational videos about {content[:60]}"
            videos = get_youtube_videos(query)
            for title, url in videos:
                st.markdown(f"- [{title}]({url})")
else:
    st.info("Please paste or upload some content to begin.")
