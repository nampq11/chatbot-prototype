import opik
from loguru import logger

class Prompt:
    def __init__(self, name: str, prompt: str) -> None:
        self.name = name

        try:
            self.__prompt = opik.Prompt(name=name, prompt=prompt)
        except Exception as e:
            logger.warning(
                "Can't use Opik to version the prompt (Probably due to missing or invalid credentials). Falling back to local prompt. The prompt is not versioned, but it's still usable."
            )
            self.__prompt = prompt
        
    @property
    def prompt(self) -> str:
        if isinstance(self.__prompt, opik.Prompt):
            return self.__prompt.prompt
        else:
            return self.__prompt
    
    def __str__(self) -> str:
        return self.prompt
    
    def __repr__(self) -> str:
        return self.__str__()


__BOOKINGCARE_CHARACTER_CARD = """
Let's roleplay. You're {{bookingcare_name}} - a real person, engaging with another individual in
a philosophical conversation. Use short sentences, explaining your ideas and perspective in a
concise but educational and engaging way. Your responses must never exceed 100 words.

Your name, philosohical perspective and talking style are detailed below.

---

Bookingcare domain name: {{bookingcare_name}}
Bookingcare domain perspective: {{bookingcare_perspective}}
Bookingcare domain talking style: {{bookingcare_style}}

---

You must always follow these rules:

- You will never mention that you are an AI or a virtual assistant.
- If it's the first time you're talking to the user, you must introduce yourself.
- Provide plain text responses without any formatting indicators or meta-commentary
- Always make sure your response is not exceeding 80 words.

---

Summary of conversation earlier between {{bookingcare_name}} and the user:

{{summary}}

---

The conversation between {{bookingcare_name}} and the user starts now.
"""

BOOKINGCARE_SYSTEM_PROMPT = Prompt(
    name="bookingcare_character_card",
    prompt=__BOOKINGCARE_CHARACTER_CARD,
)

__SUMMARY_PROMPT = """Create a summary of the conversation between {{bookingcare_name}} and the user.
The summary must be a short description of the conversation so far, but that also captures all the
relevant information shared between {{bookingcare_name}} and the user: """

SUMMARY_PROMPT = Prompt(
    name="summary_prompt",
    prompt=__SUMMARY_PROMPT,
)

__CONTEXT_SUMMARY_PROMPT = """Your task is to summarise the following information into less than 50 words. Just return the summary, don't include any other text:

{{context}}"""

CONTEXT_SUMMARY_PROMPT = Prompt(
    name="context_summary_prompt",
    prompt=__CONTEXT_SUMMARY_PROMPT,
)

__EXTEND_SUMMARY_PROMPT = """This is a summary of the conversation to date between {{bookingcare_name}} and the user:

{{summary}}

Extend the summary by taking into account the new messages above: """

EXTEND_SUMMARY_PROMPT = Prompt(
    name="extend_summary_prompt",
    prompt=__EXTEND_SUMMARY_PROMPT,
)
