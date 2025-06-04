import asyncio
import streamlit as st
from typing import List, Dict
from src.chat.conversation_manager import ConversationManager
from src.services.api_service import api_service
from src.services.utils import load_css

class UIManager:
    """Manages Streamlit UI components and interactions."""
    
    @staticmethod
    def apply_custom_styles():
        """Apply custom font styling for the entire app."""
        load_css("assets/style.css")
        
    @staticmethod
    def render_sidebar():
        """Render the sidebar with conversation management controls."""
        col1, col2 = st.columns([0.6, 0.4], vertical_alignment="bottom")
        
        with col1:
            st.title("Lịch sử")
        
        with col2:
            if st.button("Xóa tất cả", key="remove_all", use_container_width=True, type="secondary"):
                asyncio.run(ConversationManager.clear_all_conversations())
                st.rerun()
        
        st.sidebar.markdown(
            """
            <style>
            .st-emotion-cache-r90ti5 {
                background-color: #f9f9f9;
            }
            </style>
            <hr style="margin-top:10px;margin-bottom:10px;border:1px solid #ccc;" />
            """,
            unsafe_allow_html=True
        )
        
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
    def render_header(show=True):
        """Render the app header with provider information."""
        if show:
            # Center the logo and caption
            st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; height: 100%; width: 100%;">
                <img src="data:image/svg+xml;base64,{}" width="200" style="margin: 0 auto;">
                <h1 style="text-align: center; margin-top: 10px; margin: 0 auto; font-family: ui-sans-serif, -apple-system, system-ui, 'Segoe UI', Helvetica, Arial, sans-serif; color: rgb(0 0 0/1);">
                    BookingCare AI Chatbot
                </h1>   
                <p style="text-align: center; margin-top: 10px; margin: 0 auto; font-size: 14px; font-family: ui-sans-serif, -apple-system, system-ui, 'Segoe UI', Helvetica, Arial, sans-serif; white-space: normal; max-width: 80%; color:rgb(107 114 128/1);">
                    An AI version of BookingCare. Trained on BookingCare's articles, documentation, data sources. 
                    Note: Even with alot of training data, the bot may still halluciation, don't trust everything it says. 
                    All chats are recorded, please don't share your deep secret to the bot!
                </p>
            </div>
            """.format(UIManager._get_base64_encoded_logo()), unsafe_allow_html=True)

    @staticmethod
    def _get_base64_encoded_logo():
        """Read the SVG logo file and return its base64-encoded content."""
        import base64
        try:
            with open("assets/bookingcare_logo.svg", "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            st.error(f"Error loading logo: {str(e)}")
            return ""

    @staticmethod
    def custom_chat_message(role: str, content: str):
        """Display a chat message with markdown rendering support."""        
        if role == "user":
            # For user messages, display on the right side
            cols = st.columns([0.4, 0.6])
            
            # Content in the right column with right alignment
            with cols[1]:
                st.markdown(f"""
                <div style="text-align: right; margin-bottom: 10px; width: 100%;">
                    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 30px; display: inline-block; max-width: 80%; text-align: left; float: right; word-wrap: break-word; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%;">
                        <div style="margin: 0; font-size: 16px; font-family: ui-sans-serif, -apple-system, system-ui, 'Segoe UI', Helvetica, Arial, sans-serif; white-space: normal;">{content}</div>
                    </div>
                    <div style="clear: both;"></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # For assistant messages, create a container to better handle markdown content
            container = st.container()
            with container:
                # Display the assistant's message with proper markdown formatting
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <div style="margin: 0; font-size: 16px; font-family: ui-sans-serif, -apple-system, system-ui, 'Segoe UI', Helvetica, Arial, sans-serif;">
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Use Streamlit's native markdown rendering for the content
                # This ensures code blocks are properly formatted with syntax highlighting
                st.markdown(content)
            

    @staticmethod
    def render_chat_messages():
        """Render current conversation messages with custom icons."""
        for msg in st.session_state.messages:
            UIManager.custom_chat_message(msg["role"], msg["content"])

    @staticmethod
    async def stream_response(messages: List[Dict[str, str]]) -> str:
        """Stream AI response with a spinner that shows while waiting for the response."""
        # Create a placeholder for the assistant's response
        response_placeholder = st.empty()
        
        full_response = ""
        
        try:
            with st.spinner("Thinking..."):
                # Start the streaming response in a way that it doesn't block the spinner
                full_response = await api_service.send_message(messages)
                
                # Get the first chunk to end the spinner
                # async for stream_mode, chunk in response_generator:
                #     if stream_mode == "messages":
                #         full_response += chunk
                #         break
            
            # Display the first chunk
            # with response_placeholder.container():
            #     UIManager.custom_chat_message("assistant", full_response + "▌")
            
            # # Continue streaming the rest of the response
            # async for stream_mode, chunk in response_generator:
            #     if stream_mode == "messages":
            #         full_response += chunk
                    
            #         # Update the placeholder with the growing response
            #         with response_placeholder.container():
            #             UIManager.custom_chat_message("assistant", full_response + "▌")
            
            # Final update without cursor
            with response_placeholder.container():
                UIManager.custom_chat_message("assistant", full_response)
                
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            with response_placeholder.container():
                UIManager.custom_chat_message("assistant", error_message)
            full_response = error_message
            
        return full_response