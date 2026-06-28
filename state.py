"""
Task 2: State structure for the Customer Support Automation System.
"""

from typing import TypedDict, Optional, List, Literal


class SupportState(TypedDict):
    # Customer info
    customer_id: str
    customer_name: Optional[str]

    # Query
    query: str
    intent: Optional[Literal["sales", "technical", "billing", "account", "memory"]]

    # RAG context retrieved from knowledge base
    retrieved_context: Optional[str]

    # Agent response before supervisor review
    draft_response: Optional[str]

    # Final response sent to customer
    final_response: Optional[str]

    # Human-in-the-loop
    requires_human_approval: bool
    human_approved: Optional[bool]
    human_feedback: Optional[str]

    # Conversation history (from SQLite, loaded at runtime)
    conversation_history: List[dict]

    # Routing metadata
    escalation_reason: Optional[str]
    error: Optional[str]
