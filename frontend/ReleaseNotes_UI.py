import os
import sys

from backend.trainAndTest import testingJsonWithClaude

# Add the *project root* to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ChatBot import call_claude_sonnet
import streamlit as st

result = "content='April 16, 2025\n**[Image here]**\n Vroozi April 2025\n Release Notes\nTable of Contents:\nMulti-Unit ID Management 2\n Enhanced User and Business Unit Management Across Multiple Units 2\n Improved Navigation and Access Control 2\nSupplier Discovery Module (SDM) 3\n User Group-Based Access Control 3\n Enhanced Supplier Management 3\nResolutions 4\n\n# Multi-Unit ID Management\n## ENHANCED USER AND BUSINESS UNIT MANAGEMENT ACROSS MULTIPLE UNITS\nVroozi has introduced comprehensive multi-unit ID management capabilities to help\norganizations efficiently manage users and configurations across multiple business\nunits:\n\n- Master Admin Controls: Master administrators can now manage user access,\n configurations and settings across all linked business units from a centralized\n parent unit.\n- User Group Management: Improved user group management with the ability to\n create, edit and assign users to specific business unit groups.\n- SSO Configuration: Centralized SSO settings management from the parent unit\n that propagates to all child units.\n- Profile Management: Users can now edit their profiles from both parent and\n child units with appropriate access controls.\n\n## IMPROVED NAVIGATION AND ACCESS CONTROL\nThe new multi-unit navigation and access control features include:\n\n- Business Unit Switching: Users can easily switch between business units they\n have access to using an intuitive dropdown menu.\n- Context Awareness: A persistent header clearly indicates which business unit\n the user is currently working in.\n- Granular Permissions: Master admins can control which business units and\n features each user can access.\n- Audit Trail: Comprehensive tracking of user access changes and activities\n across business units.\n\n# Supplier Discovery Module (SDM)\n## USER GROUP-BASED ACCESS CONTROL\nThe SDM now supports role-based access control through user groups:\n\n- Configurable Access: Administrators can define which suppliers and features\n users can access based on their assigned user group.\n- Dynamic Role Labels: Role names and prefixes automatically update based on\n user group settings.\n- Filtered Views: Search results and supplier lists are automatically filtered\n based on user group permissions.\n\n## ENHANCED SUPPLIER MANAGEMENT\nImprovements to supplier management in SDM include:\n\n- Bulk Operations: Enhanced bulk upload/download capabilities that respect user\n group permissions.\n- Location Management: Improved location filtering and management based on\n user groups.\n- Supplier Association: Ability to associate suppliers with multiple user groups\n for flexible access control.\n\n# Resolutions\n- Fixed an issue where supplier custom field associations were not saving\n properly.\n- Resolved a bug preventing SDM users from being opened from PMAN Master\n Data.\n- Fixed user creation modal display issues in SDM/PMAN.\n- Corrected location creation validation to properly handle company code active\n status.\n- Resolved issues with tax code and withholding tax management.\n- Fixed performance issues with sorting and pagination in invoice management.\n- Improved handling of catalog item references in purchase requests.\n- Enhanced error handling for external accounting validation workflows.' additional_kwargs={} response_metadata={'id': 'msg_01HocDidqnU9xpoYKYds7CSP', 'model': 'claude-3-5-sonnet-20241022', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'input_tokens': 141760, 'output_tokens': 715}, 'model_name': 'claude-3-5-sonnet-20241022'} id='run-bd773fe8-250d-4bf7-9585-3b70764328ed-0' usage_metadata={'input_tokens': 141760, 'output_tokens': 715, 'total_tokens': 142475, 'input_token_details': {'cache_read': 0, 'cache_creation': 0}}"


def load_css(file_path):
    with open(file_path, "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


load_css("frontend/CSS/style.css")


def release_notes_page():
    st.markdown("<h1 class='st-title'>📝 Release Notes Analysis</h1>", unsafe_allow_html=True)

    release_name = st.text_input("🏷️ Enter Release Name:")
    prompt = st.text_area("📌 Enter Prompt:", height=150)

    # ✨ Generate Analysis
    if st.button("✨ Generate Analysis"):
        if prompt and release_name:
            response = testingJsonWithClaude(release_name, prompt)
            st.session_state["llm_response"] = response.content if hasattr(response, "content") else str(response)
        else:
            st.warning("⚠️ Please enter both Prompt and Release Name.")

    # Show formatted response and download option
    if "llm_response" in st.session_state:
        st.markdown("### 🤖 LLM Response (Formatted Output):")
        st.markdown(st.session_state["llm_response"])


def chatbot_page():
    st.markdown("<h1 class='st-title'>💬 VROOZI ChatBot</h1>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "👋 Hello! Ask me anything about VROOZI."}]
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
