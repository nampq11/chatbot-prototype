import litellm
import streamlit as st
from google import genai
from src.config import Config
import os
import uuid

config = Config()

# Initialize session state for conversations if it doesn't exist
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = {}  # Dictionary to store conversations

if "current_conversation_id" not in st.session_state:
    # Generate a unique ID for the initial conversation
    new_id = str(uuid.uuid4())
    st.session_state["current_conversation_id"] = new_id
    st.session_state["conversation_history"][new_id] = {
        "title": "New Conversation",
        "messages": [{"role": "assistant", "content": "How can I help you?"}]
    }

# Initialize messages for the current conversation if needed
if "messages" not in st.session_state:
    current_id = st.session_state["current_conversation_id"]
    st.session_state["messages"] = st.session_state["conversation_history"][current_id]["messages"]

provider = None
try:
    azure_credentials = st.secrets.get("azure_credential", {})
    AZURE_API_KEY = azure_credentials.get("AZURE_API_KEY", "")
    AZURE_BASE_URL = azure_credentials.get("AZURE_BASE_URL", "")
    AZURE_API_VERSION = azure_credentials.get("AZURE_API_VERSION", "")
    
    if AZURE_API_KEY and AZURE_BASE_URL and AZURE_API_VERSION:
        provider = "Azure OpenAI"
        st.success(f"✅ Using {provider} service")

        st.session_state["azure_api_key_value"] = AZURE_API_KEY
        st.session_state["azure_endpoint_value"] = AZURE_BASE_URL
        st.session_state["azure_deployment_value"] = AZURE_API_VERSION
        st.session_state["azure_keys_saved"] = True
except Exception as e:
    st.error(f"Error loading Azure credentials: {str(e)}")

if not provider:
    try:
        openai_credentials = st.secrets.get("openai_credential", {})
        openai_api_key = openai_credentials.get("OPENAI_API_KEY", "")
        
        if openai_api_key:
            provider = "OpenAI"
            st.success(f"✅ Using {provider} service")
            st.session_state["openai_api_key_value"] = openai_api_key
            st.session_state["openai_key_saved"] = True
            os.environ["OPENAI_API_KEY"] = openai_api_key
    except Exception as e:
        st.error(f"Error loading OpenAI credentials: {str(e)}")

if not provider:
    try:
        gemini_credentials = st.secrets.get("gemini_credential", {})
        gemini_api_key = gemini_credentials.get("GEMINI_API_KEY", "")
        
        if gemini_api_key:
            provider = "Gemini"
            st.success(f"✅ Using {provider} service")
            st.session_state["gemini_api_key_value"] = gemini_api_key
            st.session_state["gemini_key_saved"] = True
    except Exception as e:
        st.error(f"Error loading Gemini credentials: {str(e)}")

if not provider:
    st.warning("No API credentials found in configuration. Please enter your credentials:")
    provider_options = ["OpenAI", "Azure OpenAI", "Gemini"]
    manual_provider = st.selectbox(
        "Select AI Provider",
        provider_options,
        key="manual_provider_selection"
    )
    
    if manual_provider == "OpenAI":
        saved_key = config.get_api_key(manual_provider)
        key_saved = st.session_state.get("openai_key_saved", False)
        
        if key_saved and saved_key["openai_api_key"]:
            st.success("✅ OpenAI API Key saved")
            openai_api_key = saved_key["openai_api_key"]
            
            if st.button("Reset OpenAI API Key"):
                st.session_state["openai_key_saved"] = False
                st.session_state["openai_api_key"] = ""
                st.rerun()
        else:
            openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
            "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            if openai_api_key and st.button("Save OpenAI API Key"):
                config.save_api_key(manual_provider, openai_api_key=openai_api_key)
                provider = "OpenAI"
                st.rerun()
        
        os.environ["OPENAI_API_KEY"] = st.session_state.get("openai_api_key_value", "")
    
    elif manual_provider == "Azure OpenAI":
        saved_keys = config.get_api_key(manual_provider)
        keys_saved = st.session_state.get("azure_keys_saved", False)
        
        if keys_saved and saved_keys["AZURE_API_KEY"]:
            st.success("✅ Azure OpenAI credentials saved")
            AZURE_API_KEY = saved_keys["AZURE_API_KEY"]
            AZURE_BASE_URL = saved_keys["AZURE_BASE_URL"]
            AZURE_API_VERSION = saved_keys["AZURE_API_VERSION"]

            if st.button("Reset Azure OpenAI Credentials"):
                st.session_state["azure_keys_saved"] = False
                st.session_state["azure_api_key"] = ""
                st.session_state["azure_endpoint"] = ""
                st.session_state["azure_deployment"] = ""
                st.rerun()
        else:
            AZURE_API_KEY = st.text_input("Azure OpenAI API Key", key="azure_api_key", type="password")
            AZURE_BASE_URL = st.text_input("Azure OpenAI Endpoint", key="azure_endpoint")
            AZURE_API_VERSION = st.text_input("Azure Deployment Name", key="azure_deployment")
            "[Learn about Azure OpenAI Service](https://github.com/andrewyng/aisuite/blob/main/guides/azure.md)"
            if AZURE_API_KEY and AZURE_BASE_URL and AZURE_API_VERSION and st.button("Save Azure OpenAI Credentials"):
                config.save_api_key(manual_provider, AZURE_API_KEY=AZURE_API_KEY, AZURE_BASE_URL=AZURE_BASE_URL, AZURE_API_VERSION=AZURE_API_VERSION)
                provider = "Azure OpenAI"
                st.rerun()
    
    elif manual_provider == "Gemini":
        saved_key = config.get_api_key(manual_provider)
        key_saved = st.session_state.get("gemini_key_saved", False)
        
        if key_saved and saved_key["gemini_api_key"]:
            st.success("✅ Gemini API Key saved")
            gemini_api_key = saved_key["gemini_api_key"]

            if st.button("Reset Gemini API Key"):
                st.session_state["gemini_key_saved"] = False
                st.session_state["gemini_api_key"] = ""
                st.rerun()
        else:
            gemini_api_key = st.text_input("Gemini API Key", key="gemini_api_key", type="password")
            "[Get a Gemini API key](https://aistudio.google.com/app/apikey)"
            if gemini_api_key and st.button("Save Gemini API Key"):
                config.save_api_key(manual_provider, gemini_api_key=gemini_api_key)
                provider = "Gemini"
                st.rerun()

st.title("💬 Chatbot")
st.caption(f"🚀 A Streamlit chatbot powered by {provider}")

# Sidebar for conversation management
with st.sidebar:
        # Apply CSS to hide button border
    st.markdown("""
    <style>
    div[data-testid="stButton"] button[kind="secondary"] {
        border: none;
        background-color: transparent;
        color: #FF4B4B;
        padding: 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button(icon=":material/add_circle:",label="Cuộc trò chuyện mới", key="new_conversation", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state["conversation_history"][new_id] = {
        "title": "Cuộc trò chuyện mới",
        "messages": [{"role": "assistant", "content": "Tôi có thể giúp gì cho bạn?"}]
        }
        st.session_state["current_conversation_id"] = new_id
        st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
        st.rerun()
    
    col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")
    
    with col1:
        st.title("Lịch sử")
    
    with col2:
        if st.button("Xóa tất cả", key="remove_all", use_container_width=True, type="secondary"):
        # Create a new conversation
            new_id = str(uuid.uuid4())
            # Clear conversation history
            st.session_state["conversation_history"] = {
                new_id: {
                    "title": "Cuộc trò chuyện mới",
                    "messages": [{"role": "assistant", "content": "Tôi có thể giúp gì cho bạn?"}]
                }
            }
            # Set as current conversation
            st.session_state["current_conversation_id"] = new_id
            st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
            st.rerun()

    st.sidebar.markdown("""<hr style="margin-top:10px;margin-bottom:10px;border:1px solid #ccc;" />""", unsafe_allow_html=True)

    # Check if there are any conversations to display
    if len(st.session_state["conversation_history"]) > 0:
        # Sort conversations by recency (if you want to add timestamps later)
        for conv_id, conv_data in st.session_state["conversation_history"].items():
            # Get the title or first few words of first user message as the title
            title = conv_data["title"]
            
            # Create columns for the conversation title and delete button
            col1, col2 = st.columns([0.8, 0.2])
            
            # Show conversation title as a button to select it
            if col1.button(title, key=f"conv_{conv_id}"):
                st.session_state["current_conversation_id"] = conv_id
                st.session_state["messages"] = st.session_state["conversation_history"][conv_id]["messages"]
                st.rerun()
            
            # Add delete button for individual conversations
            if col2.button(icon=":material/close:", label="", key=f"delete_{conv_id}"):
                # Delete this conversation
                del st.session_state["conversation_history"][conv_id]
                
                # If we deleted the current conversation, switch to another one or create a new one
                if conv_id == st.session_state["current_conversation_id"]:
                    if st.session_state["conversation_history"]:
                        # Switch to any existing conversation
                        new_id = next(iter(st.session_state["conversation_history"]))
                        st.session_state["current_conversation_id"] = new_id
                        st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
                    else:
                        # Create a new conversation if none left
                        new_id = str(uuid.uuid4())
                        st.session_state["conversation_history"][new_id] = {
                            "title": "Cuộc trò chuyện mới",
                            "messages": [{"role": "assistant", "content": "Tôi có thể giúp gì cho bạn?"}]
                        }
                        st.session_state["current_conversation_id"] = new_id
                        st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
                st.rerun()
    else:
        st.sidebar.text("Không có lịch sử trò chuyện")
    
    # Remove all conversations button


# Display current conversation
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not provider:
        st.error("No AI provider configured. Please check your configuration or enter API credentials in the sidebar.")
        st.stop()
    
    # Get API credentials based on selected provider
    if provider == "OpenAI":
        openai_api_key = config.get_api_key(provider)["openai_api_key"]
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
    elif provider == "Azure OpenAI":
        azure_creds = config.get_api_key(provider)
        AZURE_API_KEY = azure_creds["AZURE_API_KEY"]
        AZURE_BASE_URL = azure_creds["AZURE_BASE_URL"]
        AZURE_API_VERSION = azure_creds["AZURE_API_VERSION"]
        if not (AZURE_API_KEY and AZURE_BASE_URL and AZURE_API_VERSION):
            st.info("Please add your Azure OpenAI details to continue.")
            st.stop()
    elif provider == "Gemini":
        gemini_api_key = config.get_api_key(provider)["gemini_api_key"]
        if not gemini_api_key:
            st.info("Please add your Gemini API key to continue.")
            st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Update the conversation title if this is the first user message
    current_id = st.session_state["current_conversation_id"]
    conversation = st.session_state["conversation_history"][current_id]
    # Use the first few words of the first user message as the conversation title
    user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
    if len(user_messages) == 1:  # This is the first user message
        # Take first 5 words or fewer for the title
        title_text = " ".join(user_messages[0]["content"].split()[:5])
        if len(title_text) > 30:
            title_text = title_text[:27] + "..."
        conversation["title"] = title_text
    
    # Update the conversation in history
    st.session_state["conversation_history"][current_id]["messages"] = st.session_state.messages
    
    st.chat_message("user").write(prompt)
    
    assistant_response_placeholder = st.chat_message("assistant").empty()
    full_response = ""
    
    if provider == "OpenAI":
        for chunk in litellm.completion(
            model="gpt-4.1-nano",
            messages=st.session_state.messages,
            stream=True,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk
                assistant_response_placeholder.markdown(full_response + "▌")
        
        assistant_response_placeholder.markdown(full_response)
    
    elif provider == "Azure OpenAI":
        for chunk in litellm.completion(
            model="azure/gpt-4.1-nano",
            api_key=AZURE_API_KEY,
            api_base=AZURE_BASE_URL,
            api_version=AZURE_API_VERSION,
            messages=st.session_state.messages,
            stream=True,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk
                assistant_response_placeholder.markdown(full_response + "▌")
        
        assistant_response_placeholder.markdown(full_response)
    
    elif provider == "Gemini":
        try:
            genai.configure(api_key=gemini_api_key)
            
            model = genai.GenerativeModel('gemini-pro')
            
            gemini_messages = []
            for message in st.session_state.messages:
                role = "user" if message["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [message["content"]]})
            
            response = model.generate_content(gemini_messages, stream=True)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    full_response += chunk.text
                    assistant_response_placeholder.markdown(full_response + "▌")
            
            assistant_response_placeholder.markdown(full_response)
            
        except ImportError:
            error_msg = "Error: google-genai package not installed. Please contact the administrator."
            full_response = error_msg
            assistant_response_placeholder.markdown(error_msg)
        except Exception as e:
            error_msg = f"I encountered an error while processing your request: {str(e)}"
            full_response = error_msg
            assistant_response_placeholder.markdown(error_msg)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
