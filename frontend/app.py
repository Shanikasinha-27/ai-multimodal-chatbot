import os
import requests
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Aura | Multimodal Emotional Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Custom CSS for soothing, empathetic styling
st.markdown("""
<style>
    .main-header {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2E4053;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #5D6D7E;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .crisis-card {
        background-color: #FDEDEC;
        border-left: 5px solid #E74C3C;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .rag-card {
        background-color: #EAF2F8;
        border-left: 4px solid #3498DB;
        padding: 10px 15px;
        border-radius: 6px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Session State Initialization -----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions_list" not in st.session_state:
    st.session_state.sessions_list = []

# Helper Functions
def fetch_sessions():
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/sessions", timeout=3)
        if res.status_code == 200:
            st.session_state.sessions_list = res.json()
    except Exception:
        pass

def create_new_session(title="New Conversation"):
    try:
        res = requests.post(
            f"{API_BASE_URL}/api/v1/sessions",
            json={"title": title},
            timeout=3
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.messages = []
            fetch_sessions()
    except Exception as e:
        st.error(f"Could not connect to FastAPI backend at {API_BASE_URL}. Ensure it is running.")

def load_session_messages(session_id: str):
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/sessions/{session_id}/messages", timeout=3)
        if res.status_code == 200:
            msgs = res.json()
            st.session_state.messages = []
            for m in msgs:
                st.session_state.messages.append({
                    "sender": m["sender_type"],
                    "text": m["text_content"],
                    "media_type": m["media_type"],
                    "media_url": m["media_url"],
                    "guardrail_flagged": m["guardrail_flagged"],
                    "retrieved": []
                })
    except Exception as e:
        st.error(f"Failed to fetch session messages: {e}")

# Initial load
if not st.session_state.session_id:
    fetch_sessions()
    if st.session_state.sessions_list:
        st.session_state.session_id = st.session_state.sessions_list[0]["session_id"]
        load_session_messages(st.session_state.session_id)
    else:
        create_new_session()

# ----------------- Sidebar -----------------
with st.sidebar:
    st.title("🌿 Aura Companion")
    st.caption("Multimodal Emotional Support & Mindful Grounding")
    
    # Crisis Safety Card (Always visible)
    st.markdown("""
    <div class="crisis-card">
        <strong>🆘 Need Immediate Support?</strong><br>
        • <strong>Call / Text:</strong> 988 (24/7 Lifeline)<br>
        • <strong>Text:</strong> HOME to 741741<br>
        • <strong>Global:</strong> <a href="https://findahelpline.com" target="_blank">findahelpline.com</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # Session Management
    st.subheader("💬 Conversations")
    if st.button("➕ Start New Conversation", use_container_width=True):
        create_new_session()
        st.rerun()

    # Session list
    if st.session_state.sessions_list:
        session_options = {s["session_id"]: s["session_title"] for s in st.session_state.sessions_list}
        selected_sid = st.selectbox(
            "Select Session",
            options=list(session_options.keys()),
            format_func=lambda x: session_options.get(x, "Conversation"),
            index=list(session_options.keys()).index(st.session_state.session_id) if st.session_state.session_id in session_options else 0
        )
        if selected_sid != st.session_state.session_id:
            st.session_state.session_id = selected_sid
            load_session_messages(selected_sid)
            st.rerun()

    st.divider()

    # Voice / Audio Settings
    enable_voice = st.checkbox("🔊 Spoken Voice Responses (TTS)", value=True, help="Synthesizes voice audio response alongside text")

    st.divider()

    # RAG Knowledge Ingestion
    with st.expander("📚 Add Support Guide (RAG)"):
        st.caption("Upload or paste self-care practices into the knowledge base.")
        guide_title = st.text_input("Guide Title", placeholder="e.g. Somatic Grounding Exercise")
        guide_category = st.selectbox("Category", ["grounding", "cbt", "mindfulness", "general_support"])
        guide_content = st.text_area("Content", placeholder="Step-by-step instructions...")
        if st.button("Save to Knowledge Base"):
            if guide_title and guide_content:
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/api/v1/rag/upload",
                        json={"title": guide_title, "category": guide_category, "content": guide_content},
                        timeout=5
                    )
                    if res.status_code == 200:
                        st.success("Guide successfully indexed in RAG!")
                    else:
                        st.error("Failed to index guide.")
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.warning("Please provide both title and content.")

# ----------------- Main Chat View -----------------
st.markdown("<h2 class='main-header'>🌿 Aura: Your Mindful Companion</h2>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>A safe, compassionate space to share your thoughts, photos, and voice notes.</p>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.messages:
    role = "user" if msg["sender"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🌿"
    
    with st.chat_message(role, avatar=avatar):
        # Render text
        if msg.get("text"):
            st.markdown(msg["text"])
        
        # Render user image preview if present
        if msg.get("media_type") == "image" and msg.get("media_url"):
            full_img_url = f"{API_BASE_URL}{msg['media_url']}"
            st.image(full_img_url, caption="Uploaded image", width=300)
            
        # Render audio player if present
        if msg.get("media_type") == "audio" and msg.get("media_url"):
            full_aud_url = f"{API_BASE_URL}{msg['media_url']}"
            st.audio(full_aud_url)

        # Render RAG recommendations if assistant returned any
        if msg.get("retrieved"):
            with st.expander("💡 Coping & Grounding References"):
                for entry in msg["retrieved"]:
                    st.markdown(f"**{entry.get('title')}** ({entry.get('category')})")
                    st.write(entry.get("content"))

# ----------------- Multimodal Input Area -----------------
with st.expander("📎 Attach Media (Image or Voice Note)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        uploaded_image = st.file_uploader("Upload an Image (e.g. photo, artwork, journaling)", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            st.image(uploaded_image, caption="Preview", width=180)
    with col2:
        uploaded_audio = st.file_uploader("Upload a Voice Note", type=["wav", "mp3", "m4a", "ogg"])
        if uploaded_audio:
            st.audio(uploaded_audio)

# Chat text input
user_input = st.chat_input("Share what is on your mind or how you're feeling...")

if user_input or uploaded_image or uploaded_audio:
    # 1. Display user message immediately in UI
    user_media_type = "none"
    if uploaded_image:
        user_media_type = "image"
    elif uploaded_audio:
        user_media_type = "audio"

    st.session_state.messages.append({
        "sender": "user",
        "text": user_input or "[Media Upload]",
        "media_type": user_media_type,
        "media_url": None,
        "guardrail_flagged": False,
        "retrieved": []
    })

    # Prepare multipart form data for FastAPI
    form_data = {
        "session_id": st.session_state.session_id,
        "message": user_input or "",
        "enable_voice_output": str(enable_voice).lower()
    }
    files = {}
    if uploaded_image:
        files["image"] = (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)
    if uploaded_audio:
        files["audio"] = (uploaded_audio.name, uploaded_audio.getvalue(), uploaded_audio.type)

    # 2. Call FastAPI backend
    with st.spinner("Holding space and reflecting..."):
        try:
            res = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                data=form_data,
                files=files if files else None,
                timeout=60
            )

            if res.status_code == 200:
                data = res.json()
                assistant_msg = {
                    "sender": "assistant",
                    "text": data["response_text"],
                    "media_type": "audio" if data.get("audio_output_url") else "none",
                    "media_url": data.get("audio_output_url"),
                    "guardrail_flagged": data.get("guardrail_flagged", False),
                    "retrieved": data.get("retrieved_techniques", [])
                }
                st.session_state.messages.append(assistant_msg)
                fetch_sessions()
            else:
                st.error(f"Backend returned error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Connection error to backend: {e}")

    st.rerun()
