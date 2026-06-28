"""
Task 9: Supervisor agent that validates and improves responses before sending.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from config import LLM
from state import SupportState

llm = LLM

SUPERVISOR_PROMPT = """You are a Senior Customer Support Supervisor at ABC Technologies.
Your job is to review AI-drafted responses and ensure they are:
1. Accurate and based on company policy
2. Professional and empathetic in tone
3. Clear, concise, and complete
4. Appropriately handle the customer's concern

If the draft is good, return it with minor improvements.
If the draft is missing information or has issues, improve it significantly.

Always end with: "If you need further assistance, please don't hesitate to reach out!"

Return ONLY the final improved response text. No meta-commentary."""


def supervisor_agent(state: SupportState) -> SupportState:
    draft = state.get("draft_response", "")
    query = state["query"]
    intent = state.get("intent", "general")
    human_feedback = state.get("human_feedback", "")
    human_approved = state.get("human_approved")

    # Build context for supervisor
    approval_note = ""
    if state.get("requires_human_approval"):
        if human_approved:
            approval_note = f"\nNote: This request was APPROVED by human supervisor. Feedback: {human_feedback}"
        elif human_approved is False:
            approval_note = f"\nNote: This request was REJECTED by human supervisor. Reason: {human_feedback}"

    user_msg = f"""Customer Query: {query}
Department: {intent}
{approval_note}

Draft Response:
{draft}

Please review and return the final, polished response."""

    response = llm.invoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=user_msg),
    ])

    final = response.content.strip()
    print(f"[SupervisorAgent] Final response prepared.")
    return {**state, "final_response": final}
