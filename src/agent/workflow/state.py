from langgraph.graph import MessagesState

class BookingCareAgentState(MessagesState):
    bookingcare_context: str
    bookingcare_name: str
    bookingcare_perspective: str
    bookingcare_style: str
    summary: str

def state_to_str(state: BookingCareAgentState) -> str:
    if "summary" in state and bool(state["summary"]):
        conversation = state["summary"]
    elif "messages" in state and bool(state["messages"]):
        conversation = state["messages"]
    else:
        conversation = ""
    
    return f"""
BookingCareAgentState(bookingcare_context={state["bookingcare_context"]},
bookingcare_name={state["bookingcare_name"]},
bookingcare_perspective={state["bookingcare_perspective"]},
bookingcare_style={state["bookingcare_style"]},
conversation={conversation})
    """
    