from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage
import operator


class MwemaAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    thread_id: str
    user_id: Optional[str]
    language: Optional[str]  # "fr" or "en"
    current_intent: Optional[str]  # buy, book, info, general
    customer_name: Optional[str]
    customer_email: Optional[str]
    booking_service: Optional[str]
    booking_date: Optional[str]
    cart_items: Optional[list[dict]]
    response_text: Optional[str]
    checkout_url: Optional[str]
