import requests
import streamlit as st
from typing import List, Dict

class APIService:
    def __init__(self) -> None:
        self.base_url = st.secrets.backend.BACKEND_URL

    async def request(self, endpoint: str, method: str, data: dict = None) -> dict:
        """Make a request to the API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Optional data to send
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise e

    async def send_message(self, messages: List[Dict[str, str]]) -> str:
        """Send the last user message to the chat API.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Response from the API
        """
        try:
            # Get the last user message
            last_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), None)
            if not last_user_message:
                return "No user message found in conversation."
                
            data = await self.request(
                endpoint="/chat",
                method="POST", 
                data={
                    "message": last_user_message,
                    "domain_id": "healthcare",
                }
            )
            return data["response"]
        except Exception as e:
            print(f"Error sending message to API: {e}")
            return "I'm sorry, I'm having trouble connecting to the service. Please try again later."

    def get_fallback_response(self, philosopher: dict) -> str:
        """Get fallback response if API call fails.
        
        Args:
            philosopher: Philosopher info dictionary
            
        Returns:
            Fallback response message
        """
        name = philosopher.get("name", "the philosopher")
        return f"I'm sorry, {name} is unavailable at the moment. Please try again later."

    async def reset_memory(self) -> dict:
        """Reset the conversation memory.
        
        Returns:
            API response
            
        Raises:
            requests.exceptions.RequestException: If the reset fails
        """
        try:
            return await self.request(
                endpoint="/reset-memory",
                method="POST"
            )
        except requests.exceptions.RequestException as e:
            print(f"Error resetting memory: {e}")
            raise e

# Create singleton instance
api_service = APIService()