import streamlit as st
import requests
import time

API_URL = st.secrets["API_URL"]
FALLBACK_URL = st.secrets["FALLBACK_URL"]

st.set_page_config(page_title="Sentiment Chat", page_icon="💬")
st.title("💬 Sentiment Analyzer Chat")

# ----------------------------
# Session state
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# Display history
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Chat input
# ----------------------------
user_input = st.chat_input("Type a sentence to analyze sentiment...")

if user_input:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    final_text = ""

    # ----------------------------
    # Try PRIMARY API
    # ----------------------------
    try:
        response = requests.post(
            API_URL,
            json={"text": user_input},
            timeout=5
        )
        response.raise_for_status()
        result = response.json()

        sentiment = result["sentiment"]
        confidence = round(result["confidence"] * 100, 2)

        final_text = (
            f"**Sentiment:** `{sentiment}`\n\n"
            f"**Confidence:** `{confidence}%`"
        )

    # ----------------------------
    # FALLBACK API
    # ----------------------------
    except Exception:
        try:
            fallback_response = requests.get(
                FALLBACK_URL,
                timeout=5
            )
            fallback_response.raise_for_status()

            fallback_text = fallback_response.text.strip()

            final_text = (
                "⚠️ **Primary service is down**\n\n"
                f"{fallback_text}"
            )

        except Exception:
            final_text = (
                "❌ **All services are currently unavailable.**\n\n"
                "Please try again later."
            )

    # ----------------------------
    # Streaming output
    # ----------------------------
    with st.chat_message("assistant"):
        placeholder = st.empty()
        streamed = ""

        for char in final_text:
            streamed += char
            placeholder.markdown(streamed)
            time.sleep(0.015)

    # Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": final_text}
    )
