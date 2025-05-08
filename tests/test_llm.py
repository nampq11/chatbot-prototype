from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
import streamlit as st

llm = AzureChatOpenAI(
    azure_endpoint=st.secrets.azure_credential.get("AZURE_BASE_URL"),
    api_key=st.secrets.azure_credential.get("AZURE_API_KEY"),
    azure_deployment=st.secrets.azure_credential.get("AZURE_MODEL_NAME"),
    api_version=st.secrets.azure_credential.get("AZURE_API_VERSION")
)

def test_azure_chat_openai():
    # Define the prompt
    system_message = "You are a helpful assistant."
    user_message = "What is the capital of France?"

    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", user_message),
        ],
        template_format="jinja2",
    )

    # Generate a response
    response = llm.invoke(
        [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        config={
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    )
    print(response.content)
    
    # Check if the response is not empty
    assert response is not None, "Response should not be None"
    
    # Check if the response contains the expected content
    assert "Paris" in response.content, "Response should contain 'Paris'"


if __name__ == "__main__":
    test_azure_chat_openai()
    print("Test passed!")