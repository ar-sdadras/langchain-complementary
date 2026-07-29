"""
Example 03: Tool Guardrails & Human Approval Gates.
Demonstrates wrapping flaky tools with automatic retries and fallback outputs.
"""

from langcomp import ToolGuard, ApprovalGate

attempt_counter = 0


def unstable_external_api(endpoint: str) -> str:
    global attempt_counter
    attempt_counter += 1
    print(f"  [API Call Attempt {attempt_counter}] Calling endpoint: {endpoint}")
    if attempt_counter < 3:
        raise ConnectionError("Network timeout connecting to external server.")
    return f"Successfully fetched data from {endpoint}"


def sensitive_db_drop(database_name: str) -> str:
    return f"Database '{database_name}' dropped successfully."


def main():
    print("=== langcomp Example 03: Tool Guards & Approval Gates ===")

    # 1. ToolGuard Demonstration
    print("\n--- 1. Guarding Flaky Tools with Auto-Retries ---")
    guard = ToolGuard(max_retries=3, retry_delay_seconds=0.1)
    guarded_api = guard.wrap_function(unstable_external_api)

    result = guarded_api("https://api.example.com/v1/data")
    print(f"Guarded Call Result: {result}")

    # 2. ApprovalGate Demonstration
    print("\n--- 2. Human-In-The-Loop Approval Gate ---")

    def user_approval_callback(action_name: str, params: dict) -> bool:
        print(f"  [APPROVAL REQUEST] Action: '{action_name}', Params: {params}")
        # Simulating approval rule: only approve if database is a test environment
        if "test" in params.get("db_name", ""):
            print("  [DECISION] APPROVED (Test database)")
            return True
        print("  [DECISION] DENIED (Production database protected!)")
        return False

    gate = ApprovalGate(approval_func=user_approval_callback)

    # Test approving test database operation
    db_params = {"db_name": "test_db_v1"}
    if gate.check_approval("drop_database", db_params):
        res = sensitive_db_drop(db_params["db_name"])
        print(f"Action Execution Output: {res}")

    # Test denying prod database operation
    prod_params = {"db_name": "prod_users_primary"}
    if not gate.check_approval("drop_database", prod_params):
        print("Action blocked by Approval Gate: Action aborted safely.")


if __name__ == "__main__":
    main()
