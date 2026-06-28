"""
Task 3: Intent Classification node.
Classifies query into: sales, technical, billing, account, memory.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from config import LLM
from state import SupportState

llm = LLM

SYSTEM_PROMPT = """You are an intent classifier for a SaaS customer support system.

Classify the customer query into EXACTLY ONE of these categories:
- sales       : pricing, plans, product info, subscriptions
- technical   : app errors, crashes, installation, login, configuration
- billing     : invoices, payments, refunds, billing issues
- account     : password reset, profile updates, account activation/deactivation
- memory      : asking about previous interactions, past issues, history

Rules:
- If the query mentions "refund", "cancel subscription", "account closure", "compensation" → billing
- If asking about their own past queries/issues → memory
- Respond with ONLY the category word. No explanation.
"""


def classify_intent(state: SupportState) -> SupportState:
    """Classify customer query intent."""
    query = state["query"]

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Customer query: {query}"),
    ])

    intent = response.content.strip().lower()

    # Fallback guard
    valid_intents = {"sales", "technical", "billing", "account", "memory"}
    if intent not in valid_intents:
        intent = "sales"  # default fallback

    print(f"[IntentClassifier] Query: '{query}' → Intent: '{intent}'")
    return {**state, "intent": intent}
