import streamlit as st
from typing import Callable, List, Dict, Optional
from src.agent.provider_base import AIProvider
from src.agent import ProviderFactory
from src.agent.conversation_manager import ConversationManager
from src.config import Config


class UIManager:
    """Manages Streamlit UI components and interactions."""
    
    @staticmethod
    def apply_custom_styles():
        """Apply custom font styling for the entire app."""
        st.markdown("""
        <style>
            html, body, [class*="css"] {
                font-family: ui-sans-serif, -apple-system, system-ui, 'Segoe UI', Helvetica, 'Apple Color Emoji', Arial, sans-serif, 'Segoe UI Emoji', 'Segoe UI Symbol' !important;
            }
            div[data-testid="stButton"] button[kind="secondary"] {
                border: none;
                background-color: transparent;
                color: #FF4B4B;
                padding: 0;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_sidebar():
        """Render the sidebar with conversation management controls."""
        col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")
        
        with col1:
            st.title("Lịch sử")
        
        with col2:
            if st.button("Xóa tất cả", key="remove_all", use_container_width=True, type="secondary"):
                ConversationManager.clear_all_conversations()
                st.rerun()
        
        st.sidebar.markdown("""<hr style="margin-top:10px;margin-bottom:10px;border:1px solid #ccc;" />""", unsafe_allow_html=True)
        
        # Display conversation history
        if len(st.session_state["conversation_history"]) > 0:
            # Display conversations in the order they appear in the OrderedDict (newest first)
            for conv_id, conv_data in st.session_state["conversation_history"].items():
                title = conv_data["title"]
                
                # Create columns for the conversation title and delete button
                col1, col2 = st.columns([0.8, 0.2])
                
                # Show conversation title as a button to select it
                if col1.button(title, key=f"conv_{conv_id}"):
                    ConversationManager.set_current_conversation(conv_id)
                    st.rerun()
                
                # Add delete button for individual conversations
                if col2.button(icon=":material/close:", label="", key=f"delete_{conv_id}"):
                    ConversationManager.delete_conversation(conv_id)
                    st.rerun()
        else:
            st.sidebar.text("Không có lịch sử trò chuyện")

    @staticmethod
    def render_header(provider: Optional[str] = None):
        """Render the app header with provider information."""
        st.title("💬 Chatbot")
        if provider:
            st.caption(f"🚀 A Streamlit chatbot powered by {provider}")
        else:
            st.caption("🚀 A Streamlit chatbot")

    @staticmethod
    def render_chat_messages():
        """Render current conversation messages."""
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    @staticmethod
    def render_provider_selection():
        """Render provider selection UI."""
        provider_options = ProviderFactory.get_provider_names()
        manual_provider = st.selectbox(
            "Select AI Provider",
            provider_options,
            key="manual_provider_selection"
        )
        return manual_provider
    
    @staticmethod
    def check_secrets_for_provider(provider_name: str) -> bool:
        """Check if secrets.toml has valid credentials for a provider."""
        provider = ProviderFactory.create_provider(provider_name)
        if provider:
            secret_creds = provider.get_credentials_from_secrets()
            return provider.are_credentials_valid(secret_creds)
        return False
    
    @staticmethod
    def render_provider_config(provider_name: str, config: Config):
        """Render configuration UI for the selected provider."""
        provider = ProviderFactory.create_provider(provider_name)
        if not provider:
            return False
        
        # Check if credentials are in secrets.toml
        using_secrets = UIManager.check_secrets_for_provider(provider_name)
        if using_secrets:
            st.success(f"✅ {provider_name} credentials loaded from secrets.toml")
            return True
        
        # Fall back to session state
        saved_key = config.get_api_key(provider_name)
        key_saved = False
        
        if provider_name == "OpenAI":
            key_saved = st.session_state.get("openai_key_saved", False)
            
            if key_saved and saved_key.get("openai_api_key"):
                st.success("✅ OpenAI API Key saved")
                
                if st.button("Reset OpenAI API Key"):
                    st.session_state["openai_key_saved"] = False
                    st.session_state["openai_api_key"] = ""
                    st.rerun()
            else:
                st.info("OpenAI API Key not found in secrets.toml. Please enter it manually.")
                openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
                "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
                if openai_api_key and st.button("Save OpenAI API Key"):
                    provider.save_credentials_to_session(openai_api_key=openai_api_key)
                    config.save_api_key(provider_name, openai_api_key=openai_api_key)
                    return True
        
        elif provider_name == "Azure OpenAI":
            key_saved = st.session_state.get("azure_keys_saved", False)
            
            if key_saved and saved_key.get("AZURE_API_KEY"):
                st.success("✅ Azure OpenAI credentials saved")

                if st.button("Reset Azure OpenAI Credentials"):
                    st.session_state["azure_keys_saved"] = False
                    st.session_state["azure_api_key"] = ""
                    st.session_state["azure_endpoint"] = ""
                    st.session_state["azure_deployment"] = ""
                    st.rerun()
            else:
                st.info("Azure OpenAI credentials not found in secrets.toml. Please enter them manually.")
                AZURE_API_KEY = st.text_input("Azure OpenAI API Key", key="azure_api_key", type="password")
                AZURE_BASE_URL = st.text_input("Azure OpenAI Endpoint", key="azure_endpoint")
                AZURE_API_VERSION = st.text_input("Azure Deployment Name", key="azure_deployment")
                "[Learn about Azure OpenAI Service](https://github.com/andrewyng/aisuite/blob/main/guides/azure.md)"
                if AZURE_API_KEY and AZURE_BASE_URL and AZURE_API_VERSION and st.button("Save Azure OpenAI Credentials"):
                    provider.save_credentials_to_session(
                        AZURE_API_KEY=AZURE_API_KEY,
                        AZURE_BASE_URL=AZURE_BASE_URL,
                        AZURE_API_VERSION=AZURE_API_VERSION
                    )
                    config.save_api_key(
                        provider_name,
                        AZURE_API_KEY=AZURE_API_KEY,
                        AZURE_BASE_URL=AZURE_BASE_URL,
                        AZURE_API_VERSION=AZURE_API_VERSION
                    )
                    return True
        
        elif provider_name == "Gemini":
            key_saved = st.session_state.get("gemini_key_saved", False)
            
            if key_saved and saved_key.get("gemini_api_key"):
                st.success("✅ Gemini API Key saved")

                if st.button("Reset Gemini API Key"):
                    st.session_state["gemini_key_saved"] = False
                    st.session_state["gemini_api_key"] = ""
                    st.rerun()
            else:
                st.info("Gemini API Key not found in secrets.toml. Please enter it manually.")
                gemini_api_key = st.text_input("Gemini API Key", key="gemini_api_key", type="password")
                "[Get a Gemini API key](https://aistudio.google.com/app/apikey)"
                if gemini_api_key and st.button("Save Gemini API Key"):
                    provider.save_credentials_to_session(gemini_api_key=gemini_api_key)
                    config.save_api_key(provider_name, gemini_api_key=gemini_api_key)
                    return True
                    
        return False
    
    @staticmethod
    def stream_response(provider: AIProvider, messages: List[Dict[str, str]]) -> str:
        """Stream AI response with a placeholder."""
        assistant_response_placeholder = st.chat_message("assistant").empty()
        full_response = ""
        
        try:
            for content_chunk in provider.generate_response(messages):
                full_response += content_chunk
                assistant_response_placeholder.markdown(full_response + "▌")
            
            assistant_response_placeholder.markdown(full_response)
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            assistant_response_placeholder.markdown(error_message)
            full_response = error_message
            
        return full_response