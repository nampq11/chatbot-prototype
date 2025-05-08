import os
import sys
import asyncio

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.agent.generate_response import get_streaming_response, get_response


async def test_streaming_async():
    # Mock the input data
    input_data = {
        "messages": [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there! How can I help you today?"},
        ],
        'bookingcare_id': "test_bookingcare_id",
        "bookingcare_context": "",
        "bookingcare_name": "",
        "bookingcare_perspective": "",
        "bookingcare_style": "",
    }

    # # test get_response
    # response, state = await get_response(
    #     messages=input_data["messages"],
    #     bookingcare_id=input_data["bookingcare_id"],
    #     bookingcare_name=input_data["bookingcare_name"],
    #     bookingcare_perspective=input_data["bookingcare_perspective"],
    #     bookingcare_style=input_data["bookingcare_style"],
    #     bookingcare_context=input_data["bookingcare_context"],
    # )
    # print(f"Response: {response}")
    # print(f"State: {state}")

    # test get_streaming_response
    async for chunk in get_streaming_response(
        messages=input_data["messages"],
        bookingcare_id=input_data["bookingcare_id"],
        bookingcare_name=input_data["bookingcare_name"],
        bookingcare_perspective=input_data["bookingcare_perspective"],
        bookingcare_style=input_data["bookingcare_style"],
        bookingcare_context=input_data["bookingcare_context"],
    ):
        print(f"Chunk: {chunk}")

def test_streaming():
    asyncio.run(test_streaming_async())

if __name__ == "__main__":
    test_streaming()
    print("Test passed!")