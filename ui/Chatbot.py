import asyncio
import streamlit as st
from src.chat.conversation_manager import ConversationManager
from src.chat.ui_manager import UIManager

asyncio.run(ConversationManager.initialize_session_state())

UIManager.apply_custom_styles()

# Check if the user has entered any text by checking if there are any user messages
show_header = True
if 'messages' in st.session_state:
    # If there are any user messages in the conversation, hide the header
    if any(message['role'] == 'user' for message in st.session_state.messages):
        show_header = False

UIManager.render_header(show_header)

with st.sidebar:
    if st.button(icon=":material/add_circle:", label="Cuộc trò chuyện mới", key="new_conversation", use_container_width=True, type="primary"):
        ConversationManager.create_new_conversation()
        st.rerun()
    
    UIManager.render_sidebar()

UIManager.render_chat_messages()

if prompt := st.chat_input(placeholder="Ask me anything"):
    
    ConversationManager.add_message("user", prompt)
    # Use custom chat message instead of the default st.chat_message
    UIManager.custom_chat_message("user", prompt)
    
    messages = ConversationManager.get_current_messages()
    full_response = asyncio.run(UIManager.stream_response(messages))
    
    ConversationManager.add_message("assistant", full_response)

