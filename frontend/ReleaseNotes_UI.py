import sys
import os

# Add the *project root* to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ChatBot import call_claude_sonnet
import streamlit as st

def load_css(file_path):
    with open(file_path, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css("frontend/CSS/style.css")

def release_notes_page():
    st.markdown("<h1 class='st-title'>📝 Release Notes Analysis</h1>", unsafe_allow_html=True)

    board_name = st.text_input("🏷️ Enter Board Name:")
    release_name = st.text_input("📌 Enter Release Name:")
    llm_response_area = st.text_area("🤖 LLM Response:", height=300)

    if st.button("✨ Generate Analysis"):
        if board_name and release_name:
            response = f"Analyzing release notes for Board: '{board_name}' and Release: '{release_name}'..."
            st.session_state["llm_response"] = response
        else:
            st.warning("⚠️ Please enter both Board Name and Release Name.")

    if "llm_response" in st.session_state:
        st.text_area("🤖 LLM Response:", st.session_state["llm_response"], height=300)
def chatbot_page():
    st.markdown("<h1 class='st-title'>💬 My Awesome Chatbot</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "👋 Hello! Ask me anything."}]
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("🗣️ Say something..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Thinking..."):
            llm_response = call_claude_sonnet(prompt)
        st.session_state["messages"].append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.markdown(llm_response)
st.sidebar.title("✨ Navigation")
page = st.sidebar.radio("Navigate to:", ["Release Notes Input", "Chatbot"])

if page == "Release Notes Input":
    release_notes_page()
elif page == "Chatbot":
    chatbot_page()