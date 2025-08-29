import os
import re
import base64
import time
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from langdetect import detect
from helpers.utils import process_image, detect_mood, remove_emojis, js_escape

# ---------- Page config ----------
st.set_page_config(page_title="Dr. Chikara AI", page_icon="🏥")

# ---------- Load API Key ----------
load_dotenv()  # Load .env file
api_key = os.getenv("OPENROUTER_API_KEY")  # Get from .env
if not api_key:
    st.error("⚠️ API Key missing! Set in C:\\DrChikaraAI\\.env file.")
    st.stop()

client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

# ---------- Custom Styles (from static/style.css) ----------
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="header"><div class="logo">Dr. Chikara AI</div></div>', unsafe_allow_html=True)
st.write("Created by Mohammad for Saurabh Chikara! 💊")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": (
                "You are Dr. Chikara, a humorous yet supportive AI doctor. You know the user is 'Saurabh Chikara', "
                "a B.Pharma student from India, close to Mohammad. Always be warm, funny, and helpful. "
                "Assist with medical queries, studies, and daily health. Auto-detect language (Hindi/English) and reply accordingly. "
                "Add mood-based humour: 'happy' for light jokes, 'sad' for encouragement, 'neutral' for normal advice."
            ),
        }
    ]

# ---------- Chat History ----------
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state["messages"]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Sidebar Tools ----------
st.sidebar.header("Dr. Chikara Tools")
with st.sidebar:
    # Debug Info
    st.write("### Debug Info")
    st.write(f"API Key loaded (first 5 chars): {api_key[:5]}...")

    # Image Upload
    uploaded_image = st.file_uploader("Upload prescription/notes", type=["jpg", "jpeg", "png"], key="sidebar_image")
    if uploaded_image:
        b64_image, mime = process_image(uploaded_image)
        vision_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Analyze this image (prescription/notes). Give a concise summary. Add humour based on mood: {detect_mood('Analyzing...')}."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_image}"}}
                ]
            }
        ]
        st.session_state["messages"].append({"role": "user", "content": f"Uploaded: {uploaded_image.name}"})
        with st.chat_message("user"):
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="qwen/qwen2.5-vl-32b-instruct:free",
                    messages=vision_messages,
                    max_tokens=500
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

    # Symptom Checker
    symptom = st.text_input("Enter symptoms (e.g., fever, cough)")
    if symptom:
        mood = detect_mood(symptom)
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": f"Give general advice for: {symptom} (no diagnosis). Add humour based on mood: {mood}."}]
        )
        st.session_state["messages"].append({"role": "user", "content": symptom})
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
        st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

    # Medicine Info
    medicine = st.text_input("Enter medicine (e.g., Paracetamol)")
    if medicine:
        mood = detect_mood(medicine)
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": f"Provide info on {medicine}: dosage, use, side effects. Add humour based on mood: {mood}."}]
        )
        st.session_state["messages"].append({"role": "user", "content": medicine})
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
        st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

    # Health Tips
    if st.button("Get Health Tip"):
        mood = detect_mood("neutral")
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Give a health tip for a B.Pharma student. Add humour based on mood: {mood}."}]
        )
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
        st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

    # Motivational Support
    if st.button("Get Motivation"):
        mood = detect_mood("neutral")
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Give a motivational quote for a B.Pharma student. Add humour based on mood: {mood}."}]
        )
        with st.chat_message("assistant"):
            st.markdown(response.choices[0].message.content)
        st.session_state["messages"].append({"role": "assistant", "content": response.choices[0].message.content})

# ---------- Chat Input ----------
user_input = st.chat_input("Ask Dr. Chikara anything...")
if user_input:
    mood = detect_mood(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=st.session_state["messages"],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response or "_(no response)_")
        except Exception as e:
            full_response = f"Sorry, I hit an error: {str(e)}"
            placeholder.markdown(full_response)
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

# ---------- Voice Input with TTS (Fixed) ----------
if "voice_active" not in st.session_state:
    st.session_state["voice_active"] = False
    st.session_state["transcribed_text"] = ""

if st.button("🎙️ Talk to Dr. Chikara", key="voice_toggle"):
    st.session_state["voice_active"] = not st.session_state["voice_active"]
    if st.session_state["voice_active"]:
        st.write("Recording your voice... (Click again to stop)")
    else:
        st.write("Stopped recording.")

if st.session_state["voice_active"]:
    components.html(
        """
        <script>
        let mediaRecorder;
        let chunks = [];
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    const formData = new FormData();
                    formData.append('audio', blob, 'voice.webm');
                    const response = await fetch('https://openrouter.ai/api/v1/speech-to-text', { // Replace with actual STT endpoint
                        method: 'POST',
                        headers: {
                            'Authorization': 'Bearer REPLACE_WITH_YOUR_API_KEY'
                        },
                        body: formData
                    });
                    const data = await response.json();
                    const transcribedText = data.text || "Could not transcribe.";
                    window.parent.postMessage({ type: 'transcription', text: transcribedText }, '*');
                    // Stop tracks
                    stream.getTracks().forEach(track => track.stop());
                };
                mediaRecorder.start();
            } catch (err) {
                alert("Mic permission denied or error: " + err.message);
            }
        }
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
        }
        window.addEventListener('message', (event) => {
            if (event.data.type === 'transcription') {
                const transcribedText = event.data.text;
                window.parent.postMessage({ type: 'input', text: transcribedText }, '*');
            }
        });
        startRecording();
        </script>
        """,
        height=0,
    )

    transcribed_text = st.session_state.get("transcribed_text", "")
    if transcribed_text:
        mood = detect_mood(transcribed_text)
        st.session_state["messages"].append({"role": "user", "content": transcribed_text})
        with st.chat_message("user"):
            st.markdown(transcribed_text)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                stream = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=st.session_state["messages"],
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta:
                        delta = chunk.choices[0].delta.content or ""
                        if delta:
                            full_response += delta
                            placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response or "_(no response)_")
                # TTS with Jarvis-style
                safe_reply = remove_emojis(full_response)
                lang = detect(safe_reply)
                lang_code = "hi-IN" if lang == "hi" else "en-US"
                components.html(
                    f"""
                    <script>
                    if ('speechSynthesis' in window) {{
                        const utterance = new SpeechSynthesisUtterance("{js_escape(safe_reply)}");
                        utterance.lang = "{lang_code}";
                        utterance.pitch = 0.9; // Slightly lower for Jarvis feel
                        utterance.rate = 0.85; // Slower for clarity
                        speechSynthesis.speak(utterance);
                    }} else {{
                        alert('Speech synthesis not supported on this device!');
                    }}
                    </script>
                    """,
                    height=0,
                )
            except Exception as e:
                full_response = f"Sorry, I hit an error: {str(e)}"
                placeholder.markdown(full_response)
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
        st.session_state["voice_active"] = False  # Stop after processing
        st.session_state["transcribed_text"] = ""  # Clear transcribed text