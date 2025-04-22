import streamlit as st
from src.config import Config
from src.agent import ProviderFactory
from src.agent.conversation_manager import ConversationManager
from src.ui_manager import UIManager

config = Config()

ConversationManager.initialize_session_state()

UIManager.apply_custom_styles()

provider = None
provider_name = None
active_provider = ProviderFactory.get_configured_provider()

if active_provider:
    provider = active_provider
    provider_name = active_provider.get_name()

# Check if the user has entered any text by checking if there are any user messages
show_header = True
if 'messages' in st.session_state:
    # If there are any user messages in the conversation, hide the header
    if any(message['role'] == 'user' for message in st.session_state.messages):
        show_header = False

UIManager.render_header(show_header)

if not provider:
    st.warning("No API credentials found in configuration. Please enter your credentials:")
    selected_provider_name = UIManager.render_provider_selection()
    
    if UIManager.render_provider_config(selected_provider_name, config):
        provider = ProviderFactory.create_provider(selected_provider_name)
        provider_name = selected_provider_name
        st.rerun()

with st.sidebar:
    if st.button(icon=":material/add_circle:", label="Cuộc trò chuyện mới", key="new_conversation", use_container_width=True, type="primary"):
        ConversationManager.create_new_conversation()
        st.rerun()
    
    UIManager.render_sidebar()

UIManager.render_chat_messages()

if prompt := st.chat_input(placeholder="Ask me anything"):
    
    if not provider:
        st.error("No AI provider configured. Please check your configuration or enter API credentials in the sidebar.")
        st.stop()
    
    if not provider.is_configured():
        st.info(provider.get_missing_config_message())
        st.stop()

    ConversationManager.add_message("user", prompt)
    # Use custom chat message instead of the default st.chat_message
    UIManager.custom_chat_message("user", prompt)
    
    messages = ConversationManager.get_current_messages()
    full_response = UIManager.stream_response(provider, messages)
    
    ConversationManager.add_message("assistant", full_response)

