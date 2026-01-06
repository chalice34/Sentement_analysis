import streamlit as st
import requests
import time

API_URL = "http://{}:8000/predict"

st.set_page_config(page_title="Sentiment Chat", page_icon="💬")

st.title("💬 Sentiment Analyzer Chat")

# ----------------------------
# Session state for chat
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Display previous messages
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Chat input
# ----------------------------
user_input = st.chat_input("Type a sentence to analyze sentiment...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call API
    try:
        response = requests.post(
            API_URL,
            json={"text": user_input},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        sentiment = result["sentiment"]
        confidence = round(result["confidence"] * 100, 2)

        final_text = (
            f"**Sentiment:** `{sentiment}`\n\n"
            f"**Confidence:** `{confidence}%`"
        )

    except Exception as e:
        final_text = f"❌ Error calling API:\n```\n{e}\n```"

    # ----------------------------
    # Streaming / typing effect
    # ----------------------------
    with st.chat_message("assistant"):
        placeholder = st.empty()
        streamed_text = ""

        for char in final_text:
            streamed_text += char
            placeholder.markdown(streamed_text)
            time.sleep(0.015)  # typing speed

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": final_text}
    )
