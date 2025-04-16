import streamlit as st
import litellm
from google import genai
import os
from src.config import Config

# Initialize config
config = Config()

with st.sidebar:
    provider = st.selectbox(
        "Select AI Provider",
        ["OpenAI", "Azure OpenAI", "Gemini"],
        key="provider_selection_search"
    )
    
    if provider == "OpenAI":
        # Check if we have saved API key
        saved_key = config.get_api_key(provider)
        key_saved = st.session_state.get("openai_key_saved", False)
        
        if key_saved and saved_key["openai_api_key"]:
            st.success("✅ OpenAI API Key saved")
            openai_api_key = saved_key["openai_api_key"]
            # Add button to reset API key
            if st.button("Reset OpenAI API Key"):
                st.session_state["openai_key_saved"] = False
                st.session_state["openai_api_key_value"] = ""
                st.rerun()
        else:
            openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key_search_input", type="password")
            "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
            if openai_api_key and st.button("Save OpenAI API Key"):
                config.save_api_key(provider, openai_api_key=openai_api_key)
                st.rerun()
        
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    elif provider == "Azure OpenAI":
        # Check if we have saved API keys
        saved_keys = config.get_api_key(provider)
        keys_saved = st.session_state.get("azure_keys_saved", False)
        
        if keys_saved and saved_keys["AZURE_API_KEY"]:
            st.success("✅ Azure OpenAI credentials saved")
            AZURE_API_KEY = saved_keys["AZURE_API_KEY"]
            AZURE_BASE_URL = saved_keys["AZURE_BASE_URL"]
            AZURE_API_VERSION = saved_keys["AZURE_API_VERSION"]
            # Add button to reset API keys
            if st.button("Reset Azure OpenAI Credentials"):
                st.session_state["azure_keys_saved"] = False
                st.session_state["azure_api_key_value"] = ""
                st.session_state["azure_endpoint_value"] = ""
                st.session_state["azure_deployment_value"] = ""
                st.rerun()
        else:
            AZURE_API_KEY = st.text_input("Azure OpenAI API Key", key="azure_api_key_search_input", type="password")
            AZURE_BASE_URL = st.text_input("Azure OpenAI Endpoint", key="azure_endpoint_search_input")
            AZURE_API_VERSION = st.text_input("Azure Deployment Name", key="azure_deployment_search_input")
            "[Learn about Azure OpenAI Service](https://github.com/andrewyng/aisuite/blob/main/guides/azure.md)"
            if AZURE_API_KEY and AZURE_BASE_URL and AZURE_API_VERSION and st.button("Save Azure OpenAI Credentials"):
                config.save_api_key(provider, AZURE_API_KEY=AZURE_API_KEY, AZURE_BASE_URL=AZURE_BASE_URL, AZURE_API_VERSION=AZURE_API_VERSION)
                st.rerun()
    
    elif provider == "Gemini":
        # Check if we have saved API key
        saved_key = config.get_api_key(provider)
        key_saved = st.session_state.get("gemini_key_saved", False)
        
        if key_saved and saved_key["gemini_api_key"]:
            st.success("✅ Gemini API Key saved")
            gemini_api_key = saved_key["gemini_api_key"]
            # Add button to reset API key
            if st.button("Reset Gemini API Key"):
                st.session_state["gemini_key_saved"] = False
                st.session_state["gemini_api_key_value"] = ""
                st.rerun()
        else:
            gemini_api_key = st.text_input("Gemini API Key", key="gemini_api_key_search_input", type="password")
            "[Get a Gemini API key](https://aistudio.google.com/app/apikey)"
            if gemini_api_key and st.button("Save Gemini API Key"):
                config.save_api_key(provider, gemini_api_key=gemini_api_key)
                st.rerun()

    # Add search options
    st.subheader("Search Options")
    search_engine = st.selectbox(
        "Search Engine",
        ["Google", "Bing", "DuckDuckGo"],
        key="search_engine"
    )
    
    num_results = st.slider("Number of search results", 1, 10, 5)

st.title("💬 Chat with Search")
st.caption(f"🚀 A Streamlit chatbot with search capabilities powered by {provider} and {search_engine}")

if "search_messages" not in st.session_state:
    st.session_state["search_messages"] = [{"role": "assistant", "content": "How can I help you? I can search the web to provide up-to-date information."}]

for msg in st.session_state.search_messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # Validate API key based on selected provider
    if provider == "OpenAI" and not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    elif provider == "Azure OpenAI" and (not AZURE_API_KEY or not AZURE_BASE_URL or not AZURE_API_VERSION):
        st.info("Please add your Azure OpenAI details to continue.")
        st.stop()
    elif provider == "Gemini" and not gemini_api_key:
        st.info("Please add your Gemini API key to continue.")
        st.stop()

    # Add user message to chat history
    st.session_state.search_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Create a placeholder for the assistant's response
    assistant_response_placeholder = st.chat_message("assistant").empty()
    full_response = ""
    
    # Here we would perform a search based on the user query
    with st.status("Searching the web..."):
        st.write(f"Using {search_engine} to search for information...")
        # Implement actual search functionality here
        st.write("Processing search results...")
    
    # Process based on selected provider with streaming
    if provider == "OpenAI":
        # Here we would combine search results with the prompt
        augmented_prompt = f"Based on the following search results, please answer: {prompt}\n\nFor demonstration purposes, we're simulating search integration."
        
        for chunk in litellm.completion(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": augmented_prompt}],
            stream=True,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk
                # Update the assistant message with accumulated response
                assistant_response_placeholder.markdown(full_response + "▌")
        
        # Final update without the cursor
        assistant_response_placeholder.markdown(full_response)
    
    elif provider == "Azure OpenAI":
        # Here we would combine search results with the prompt
        augmented_prompt = f"Based on the following search results, please answer: {prompt}\n\nFor demonstration purposes, we're simulating search integration."
        
        for chunk in litellm.completion(
            model="azure/gpt-4.1-nano",
            api_key=AZURE_API_KEY,
            api_base=AZURE_BASE_URL,
            api_version=AZURE_API_VERSION,
            messages=[{"role": "user", "content": augmented_prompt}],
            stream=True,
        ):
            if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_response += content_chunk
                # Update the assistant message with accumulated response
                assistant_response_placeholder.markdown(full_response + "▌")
        
        # Final update without the cursor
        assistant_response_placeholder.markdown(full_response)
    
    elif provider == "Gemini":
        try:
            # Here we would combine search results with the prompt
            augmented_prompt = f"Based on the following search results, please answer: {prompt}\n\nFor demonstration purposes, we're simulating search integration."
            
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Use streaming response for Gemini
            response = model.generate_content(augmented_prompt, stream=True)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    full_response += chunk.text
                    # Update the assistant message with accumulated response
                    assistant_response_placeholder.markdown(full_response + "▌")
            
            # Final update without the cursor
            assistant_response_placeholder.markdown(full_response)
            
        except Exception as e:
            error_msg = f"I encountered an error while processing your request: {str(e)}"
            full_response = error_msg
            assistant_response_placeholder.markdown(error_msg)
    
    # Add assistant response to chat history
    st.session_state.search_messages.append({"role": "assistant", "content": full_response})
