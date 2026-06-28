"""
Task 8: Human-in-the-loop approval process for high-risk requests.
Pauses workflow and waits for human supervisor input via CLI.
"""

from state import SupportState


def human_approval_node(state: SupportState) -> SupportState:
    """
    Interrupt workflow for supervisor review.
    In production: integrate with Slack/email/dashboard notification.
    Here: CLI-based approval for demonstration.
    """
    print("\n" + "=" * 60)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Customer ID    : {state['customer_id']}")
    print(f"Customer Query : {state['query']}")
    print(f"Escalation     : {state.get('escalation_reason', 'N/A')}")
    print(f"\nDraft Response :\n{state.get('draft_response', '')}")
    print("=" * 60)

    while True:
        decision = input("\nSupervisor Decision — Approve? (yes/no): ").strip().lower()
        if decision in ("yes", "y"):
            feedback = input("Optional feedback/notes (press Enter to skip): ").strip()
            print("[HumanApproval] Request APPROVED by supervisor.")
            return {
                **state,
                "human_approved": True,
                "human_feedback": feedback if feedback else "Approved by supervisor.",
            }
        elif decision in ("no", "n"):
            feedback = input("Reason for rejection: ").strip()
            print("[HumanApproval] Request REJECTED by supervisor.")
            return {
                **state,
                "human_approved": False,
                "human_feedback": feedback,
                "draft_response": f"We're sorry, but after review, we are unable to process your request at this time. Reason: {feedback}. Please contact our support team for further assistance.",
            }
        else:
            print("Please enter 'yes' or 'no'.")
