from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from src.app.agent.workflow.tools import tools
from src.config import Config
from src.domain.prompts import (
    BOOKINGCARE_SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    CONTEXT_SUMMARY_PROMPT,
    EXTEND_SUMMARY_PROMPT
)

config = Config()

def get_chat_model(
    temperature: float = 0.7,
    model_name: str = config.azure.MODEL_NAME
) -> AzureChatOpenAI:
    """Get the chat model with the specified parameters."""
    return AzureChatOpenAI(
        api_key=config.azure.API_KEY,
        azure_endpoint=config.azure.BASE_URL,
        azure_deployment=model_name,
        api_version=config.azure.API_VERSION,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        stream_usage=True
    )

def get_bookingcare_response_chain():
    model = get_chat_model()
    model = model.bind_tools(tools)
    system_message = BOOKINGCARE_SYSTEM_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message.prompt),
            MessagesPlaceholder(variable_name="messages"),
        ],
        template_format="jinja2",
    )

    return prompt | model

def get_conversation_summary_chain(
    summary: str = ""
):
    model = get_chat_model(model_name=config.azure.MODEL_NAME)

    summary_message = EXTEND_SUMMARY_PROMPT if summary else SUMMARY_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            ("human", summary_message.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model


def get_context_summary_chain():
    model = get_chat_model(model_name=config.azure.MODEL_NAME)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", CONTEXT_SUMMARY_PROMPT.prompt),
        ],
        template_format="jinja2",
    )

    return prompt | model