"""
Task 5: Specialized agents for Sales, Technical, Billing, Account support.
Also handles memory recall agent.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from config import LLM
from state import SupportState
from rag import retrieve_context
from memory import get_history, format_history_for_prompt

llm = LLM

# High-risk keywords that require human approval (Task 8)
HIGH_RISK_KEYWORDS = [
    "refund", "cancel subscription", "cancellation",
    "account closure", "close account", "compensation",
    "escalate to management", "speak to manager",
]


def _check_high_risk(query: str) -> tuple[bool, str]:
    q = query.lower()
    for kw in HIGH_RISK_KEYWORDS:
        if kw in q:
            return True, kw
    return False, ""


def _build_context(query: str) -> str:
    return retrieve_context(query)


# ─────────────────────────────────────────────
# SALES AGENT
# ─────────────────────────────────────────────
def sales_agent(state: SupportState) -> SupportState:
    query = state["query"]
    context = _build_context(query)
    history = format_history_for_prompt(state.get("conversation_history", []))

    system = """You are a friendly Sales Support agent at ABC Technologies.
Use the provided knowledge base context to answer pricing, plans, and product questions accurately.
Be concise, helpful, and professional."""

    user_msg = f"""Conversation History:
{history}

Knowledge Base Context:
{context}

Customer Query: {query}

Provide a helpful sales support response."""

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
    print(f"[SalesAgent] Drafted response.")
    return {**state, "retrieved_context": context, "draft_response": response.content.strip()}


# ─────────────────────────────────────────────
# TECHNICAL SUPPORT AGENT
# ─────────────────────────────────────────────
def technical_agent(state: SupportState) -> SupportState:
    query = state["query"]
    context = _build_context(query)
    history = format_history_for_prompt(state.get("conversation_history", []))

    system = """You are a Technical Support agent at ABC Technologies.
Use the knowledge base context to provide clear, step-by-step troubleshooting guidance.
Be precise and structured."""

    user_msg = f"""Conversation History:
{history}

Knowledge Base Context:
{context}

Customer Query: {query}

Provide technical support response with troubleshooting steps."""

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
    print(f"[TechnicalAgent] Drafted response.")
    return {**state, "retrieved_context": context, "draft_response": response.content.strip()}


# ─────────────────────────────────────────────
# BILLING AGENT
# ─────────────────────────────────────────────
def billing_agent(state: SupportState) -> SupportState:
    query = state["query"]
    context = _build_context(query)
    history = format_history_for_prompt(state.get("conversation_history", []))

    requires_approval, reason = _check_high_risk(query)

    system = """You are a Billing Support agent at ABC Technologies.
Handle invoice, payment, and billing queries professionally.
If a request requires supervisor approval, acknowledge that it will be escalated."""

    user_msg = f"""Conversation History:
{history}

Knowledge Base Context:
{context}

Customer Query: {query}

{"NOTE: This request requires human supervisor approval before processing." if requires_approval else ""}

Provide a billing support response."""

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
    print(f"[BillingAgent] Drafted response. Requires approval: {requires_approval}")

    return {
        **state,
        "retrieved_context": context,
        "draft_response": response.content.strip(),
        "requires_human_approval": requires_approval,
        "escalation_reason": reason if requires_approval else None,
    }


# ─────────────────────────────────────────────
# ACCOUNT AGENT
# ─────────────────────────────────────────────
def account_agent(state: SupportState) -> SupportState:
    query = state["query"]
    context = _build_context(query)
    history = format_history_for_prompt(state.get("conversation_history", []))

    requires_approval, reason = _check_high_risk(query)

    system = """You are an Account Support agent at ABC Technologies.
Help customers with password resets, profile updates, account activation and deactivation.
Be clear and provide exact steps."""

    user_msg = f"""Conversation History:
{history}

Knowledge Base Context:
{context}

Customer Query: {query}

{"NOTE: This request requires human supervisor approval before processing." if requires_approval else ""}

Provide account support response."""

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
    print(f"[AccountAgent] Drafted response. Requires approval: {requires_approval}")

    return {
        **state,
        "retrieved_context": context,
        "draft_response": response.content.strip(),
        "requires_human_approval": requires_approval,
        "escalation_reason": reason if requires_approval else None,
    }


# ─────────────────────────────────────────────
# MEMORY RECALL AGENT
# ─────────────────────────────────────────────
def memory_agent(state: SupportState) -> SupportState:
    customer_id = state["customer_id"]
    query = state["query"]

    history = get_history(customer_id, limit=20)
    formatted = format_history_for_prompt(history)

    system = """You are a support assistant. Use the customer's conversation history as the source of truth.
When asked about a previous support issue, review the customer's messages and directly summarize the most recent message that describes a genuine support problem or request.
If the history contains such an issue, do not say that no previous issue exists. Do not invent or infer an issue from unrelated messages.
If there is no conversation history, or the history contains no identifiable support issue, politely say that no previous support issue was found.
Be helpful, accurate, and concise."""

    user_msg = f"""Customer Conversation History:
{formatted}

Customer Query: {query}

Answer based on the conversation history above."""

    response = llm.invoke([SystemMessage(content=system), HumanMessage(content=user_msg)])
    print(f"[MemoryAgent] Recalled history for customer '{customer_id}'.")

    return {
        **state,
        "draft_response": response.content.strip(),
        "requires_human_approval": False,
    }
