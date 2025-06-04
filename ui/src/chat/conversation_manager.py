import time
import uuid
from collections import OrderedDict
from typing import List, Optional, TypedDict
import streamlit as st

from src.services.api_service import api_service

class Message(TypedDict):
    """Type definition for a chat message."""
    role: str
    content: str

class Conversation(TypedDict):
    """Type definition for a conversation."""
    title: str
    messages: List[Message]
    created_at: float

class ConversationManager:
    """Manages chat conversations and history with optimized performance and type safety."""
    
    @staticmethod
    async def initialize_session_state() -> None:
        """Initialize session state for conversations if it doesn't exist.
        
        Creates a new conversation if none exists and sets up the initial state.
        """
        if "conversation_history" not in st.session_state:
            st.session_state["conversation_history"] = OrderedDict()
            new_id = str(uuid.uuid4())
            st.session_state["current_conversation_id"] = new_id
            st.session_state["conversation_history"][new_id] = {
                "title": "Cuộc trò chuyện mới",
                "messages": [],
                "created_at": time.time()
            }
            await api_service.reset_memory()

        if "messages" not in st.session_state:
            current_id = st.session_state["current_conversation_id"]
            st.session_state["messages"] = st.session_state["conversation_history"][current_id]["messages"]
            await api_service.reset_memory()

    @staticmethod
    def _create_conversation(title: str = "Cuộc trò chuyện mới") -> tuple[str, Conversation]:
        """Create a new conversation with the given title.
        
        Args:
            title: The title for the new conversation
            
        Returns:
            tuple containing the conversation ID and the conversation data
        """
        new_id = str(uuid.uuid4())
        conversation: Conversation = {
            "title": title,
            "messages": [],
            "created_at": time.time()
        }
        return new_id, conversation

    @staticmethod
    def create_new_conversation() -> None:
        """Create a new conversation and set it as the current one.
        
        The new conversation will be placed at the beginning of the conversation history.
        """
        new_id, conversation = ConversationManager._create_conversation()
        
        # Create new ordered dictionary with the new conversation first
        new_history = OrderedDict([(new_id, conversation)])
        
        # Add existing conversations
        new_history.update(st.session_state["conversation_history"])
        
        # Update state
        st.session_state["conversation_history"] = new_history
        st.session_state["current_conversation_id"] = new_id
        st.session_state["messages"] = conversation["messages"]

    @staticmethod
    def delete_conversation(conversation_id: str) -> None:
        """Delete a conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Raises:
            KeyError: If the conversation ID doesn't exist
        """
        if conversation_id not in st.session_state["conversation_history"]:
            raise KeyError(f"Conversation {conversation_id} not found")
            
        del st.session_state["conversation_history"][conversation_id]
        
        # Handle current conversation deletion
        if conversation_id == st.session_state["current_conversation_id"]:
            if st.session_state["conversation_history"]:
                new_id = next(iter(st.session_state["conversation_history"]))
                st.session_state["current_conversation_id"] = new_id
                st.session_state["messages"] = st.session_state["conversation_history"][new_id]["messages"]
            else:
                ConversationManager.create_new_conversation()

    @staticmethod
    async def clear_all_conversations() -> None:
        """Clear all conversations and create a new one."""
        new_id, conversation = ConversationManager._create_conversation()
        st.session_state["conversation_history"] = OrderedDict([(new_id, conversation)])
        st.session_state["current_conversation_id"] = new_id
        st.session_state["messages"] = conversation["messages"]
        await api_service.reset_memory()

    @staticmethod
    def set_current_conversation(conversation_id: str) -> None:
        """Set the current conversation by ID.
        
        Args:
            conversation_id: The ID of the conversation to set as current
            
        Raises:
            KeyError: If the conversation ID doesn't exist
        """
        if conversation_id not in st.session_state["conversation_history"]:
            raise KeyError(f"Conversation {conversation_id} not found")
            
        st.session_state["current_conversation_id"] = conversation_id
        conversation = st.session_state["conversation_history"][conversation_id]
        
        if "messages" not in conversation:
            conversation["messages"] = []
            
        st.session_state["messages"] = conversation["messages"]
    
    @staticmethod
    def add_message(role: str, content: str) -> None:
        """Add a message to the current conversation.
        
        Args:
            role: The role of the message sender (e.g., 'user', 'assistant')
            content: The content of the message
        """
        if not role or not content:
            raise ValueError("Role and content cannot be empty")
            
        message: Message = {"role": role, "content": content}
        st.session_state.messages.append(message)
        
        # Update conversation in history
        current_id = st.session_state["current_conversation_id"]
        st.session_state["conversation_history"][current_id]["messages"] = st.session_state.messages
        
        # Update title for first user message
        if role == "user":
            conversation = st.session_state["conversation_history"][current_id]
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if len(user_messages) == 1:
                title_text = " ".join(user_messages[0]["content"].split()[:5])
                conversation["title"] = title_text[:27] + "..." if len(title_text) > 30 else title_text
    
    @staticmethod
    def get_current_messages() -> List[Message]:
        """Get messages in the current conversation.
        
        Returns:
            List of messages in the current conversation
        """
        return st.session_state.messages
    
    @staticmethod
    def get_last_message() -> Optional[Message]:
        """Get the last message in the current conversation.
        
        Returns:
            The last message if it exists, None otherwise
        """
        return st.session_state.messages[-1] if st.session_state.messages else None