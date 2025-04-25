import time
import uuid
from collections import OrderedDict
from typing import Dict, List, Optional
import streamlit as st


class ConversationManager:
    """Manages chat conversations and history."""
    
    @staticmethod
    def initialize_session_state() -> None:
        """Initialize session state for conversations if it doesn't exist."""
        if "conversation_history" not in st.session_state:
            st.session_state["conversation_history"] = OrderedDict()  # Use OrderedDict instead of dict
            
            # Generate a unique ID for the initial conversation
            new_id = str(uuid.uuid4())
            st.session_state["current_conversation_id"] = new_id
            # Add timestamp for sorting
            st.session_state["conversation_history"][new_id] = {
                "title": "Cuộc trò chuyện mới",
                "messages": [],
                "created_at": time.time()
            }

        # Initialize messages for the current conversation if needed
        if "messages" not in st.session_state:
            current_id = st.session_state["current_conversation_id"]
            st.session_state["messages"] = st.session_state["conversation_history"][current_id]["messages"]

    @staticmethod
    def create_new_conversation() -> None:
        """Create a new conversation and set it as the current one."""
        new_id = str(uuid.uuid4())
        
        # Create a new ordered dictionary with the new conversation first
        new_history = OrderedDict()
        
        # Add the new conversation first
        new_history[new_id] = {
            "title": "Cuộc trò chuyện mới",
            "messages": [],
            "created_at": time.time()
        }
        
        # Add all existing conversations
        for conv_id, conv_data in st.session_state["conversation_history"].items():
            new_history[conv_id] = conv_data
            
        # Update the conversation history with the new ordered dictionary
        st.session_state["conversation_history"] = new_history
        
        # Set as current conversation
        st.session_state["current_conversation_id"] = new_id
        st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]

    @staticmethod
    def delete_conversation(conversation_id: str) -> None:
        """Delete a conversation by ID."""
        if conversation_id in st.session_state["conversation_history"]:
            del st.session_state["conversation_history"][conversation_id]
            
            # If we deleted the current conversation, switch to another one or create a new one
            if conversation_id == st.session_state["current_conversation_id"]:
                if st.session_state["conversation_history"]:
                    # Switch to any existing conversation   
                    new_id = next(iter(st.session_state["conversation_history"]))
                    st.session_state["current_conversation_id"] = new_id
                    st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
                else:
                    # Create a new conversation if none left
                    ConversationManager.create_new_conversation()

    @staticmethod
    def clear_all_conversations() -> None:
        """Clear all conversations and create a new one."""
        # Create a new conversation
        new_id = str(uuid.uuid4())
        # Clear conversation history and create a new ordered dictionary with just the new conversation
        st.session_state["conversation_history"] = OrderedDict([
            (new_id, {
                "title": "Cuộc trò chuyện mới",
                "messages": [{"role": "assistant", "content": "Tôi có thể giúp gì cho bạn?"}],
                "created_at": time.time()
            })
        ])
        # Set as current conversation
        st.session_state["current_conversation_id"] = new_id
        st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]

    @staticmethod
    def set_current_conversation(conversation_id: str) -> None:
        """Set the current conversation by ID."""
        if conversation_id in st.session_state["conversation_history"]:
            st.session_state["current_conversation_id"] = conversation_id
            # Check if 'messages' key exists, if not, initialize it
            if "messages" not in st.session_state["conversation_history"][conversation_id]:
                st.session_state["conversation_history"][conversation_id]["messages"] = []
            st.session_state["messages"] = st.session_state["conversation_history"][conversation_id]["messages"]
    
    @staticmethod
    def add_message(role: str, content: str) -> None:
        """Add a message to the current conversation."""
        message = {"role": role, "content": content}
        st.session_state.messages.append(message)
        
        # Update conversation in history
        current_id = st.session_state["current_conversation_id"]
        st.session_state["conversation_history"][current_id]["messages"] = st.session_state.messages
        
        # Update the title if this is the first user message
        if role == "user":
            conversation = st.session_state["conversation_history"][current_id]
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if len(user_messages) == 1:  # This is the first user message
                # Take first 5 words or fewer for the title
                title_text = " ".join(user_messages[0]["content"].split()[:5])
                if len(title_text) > 30:
                    title_text = title_text[:27] + "..."
                conversation["title"] = title_text
    
    @staticmethod
    def get_current_messages() -> List[Dict[str, str]]:
        """Get messages in the current conversation."""
        return st.session_state.messages