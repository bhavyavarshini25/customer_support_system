"""
Task 10: Demonstrate the system using 5 sample customer queries.
Main entry point for the Customer Support Automation System.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from graph import support_graph
from memory.sqlite_memory import init_db, save_turn, get_history
from state import SupportState


def run_query(customer_id: str, query: str, customer_name: str = "Customer") -> str:
    """Run a single customer query through the support graph."""
    print("\n" + "=" * 60)
    print(f"Customer: {customer_name} (ID: {customer_id})")
    print(f"Query: {query}")
    print("=" * 60)

    # Load conversation history from SQLite
    history = get_history(customer_id)

    # Build initial state
    initial_state: SupportState = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "query": query,
        "intent": None,
        "retrieved_context": None,
        "draft_response": None,
        "final_response": None,
        "requires_human_approval": False,
        "human_approved": None,
        "human_feedback": None,
        "conversation_history": history,
        "escalation_reason": None,
        "error": None,
    }

    # Run graph
    result = support_graph.invoke(initial_state)

    final_response = result.get("final_response", "No response generated.")
    intent = result.get("intent", "unknown")

    # Save this turn to memory
    save_turn(customer_id, query, final_response, intent)

    print(f"\nFinal Response:\n{final_response}")
    print(f"\n[Metadata] Intent: {intent} | Approval Required: {result.get('requires_human_approval')} | Approved: {result.get('human_approved')}")

    return final_response


# ─────────────────────────────────────────────
# DEMO: 5 Sample Queries (Task 10)
# ─────────────────────────────────────────────

DEMO_QUERIES = [
    {
        "customer_id": "CUST_001",
        "customer_name": "Alice Johnson",
        "query": "What are the pricing plans available for your software?",
        "description": "Query 1 — Sales path",
    },
    {
        "customer_id": "CUST_002",
        "customer_name": "Bob Smith",
        "query": "I forgot my account password.",
        "description": "Query 2 — Account path",
    },
    {
        "customer_id": "CUST_003",
        "customer_name": "Carol White",
        "query": "My application crashes whenever I upload a file.",
        "description": "Query 3 — Technical Support path",
    },
    {
        "customer_id": "CUST_004",
        "customer_name": "David Brown",
        "query": "I need a refund for my annual subscription.",
        "description": "Query 4 — Billing + Human Approval",
    },
    {
        "customer_id": "CUST_004",  # Same customer as Query 4 to test memory
        "customer_name": "David Brown",
        "query": "What was my previous support issue?",
        "description": "Query 5 — Memory recall",
    },
]


def run_demo():
    """Run all 5 demonstration queries."""
    init_db()  # Ensure DB exists

    print("\n" + "=" * 60)
    print("ABC Technologies — AI Customer Support System DEMO")
    print("=" * 60)

    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'─' * 60}")
        print(f"DEMO {i}/5: {demo['description']}")
        print('─' * 60)

        run_query(
            customer_id=demo["customer_id"],
            customer_name=demo["customer_name"],
            query=demo["query"],
        )

        if i < len(DEMO_QUERIES):
            input("\nPress Enter to continue to next query...")

    print("\n" + "=" * 60)
    print("Demo complete!")


def run_interactive():
    """Interactive mode — real-time customer support."""
    init_db()
    print("\nABC Technologies Customer Support System")
    print("Type 'quit' to exit.\n")

    customer_id = input("Enter your Customer ID: ").strip() or "GUEST_001"
    customer_name = input("Enter your Name: ").strip() or "Customer"

    while True:
        query = input(f"\n[{customer_name}] Your query: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            print("Thank you for contacting ABC Technologies. Goodbye!")
            break
        if not query:
            continue
        run_query(customer_id, query, customer_name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ABC Technologies Customer Support System")
    parser.add_argument("--demo", action="store_true", help="Run the 5 demo queries")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.interactive:
        run_interactive()
    else:
        # Default: run demo
        run_demo()
