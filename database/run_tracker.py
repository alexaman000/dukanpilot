"""Persistent workflow run history tracker for DukaanPilot AI.

Records and lists persisted workflow executions in SQLite for dashboard inspection.
"""

from datetime import datetime
import os
import sqlite3
from typing import Any, Dict, List, Optional
from workflow.config import DEFAULT_DB_PATH
from workflow.state import WorkflowState


def _get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Ensure database directory exists and return SQLite connection."""
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _init_table(conn)
    return conn


def _init_table(conn: sqlite3.Connection) -> None:
    """Initialize workflow_run_history table if not already present."""
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_run_history (
                thread_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                workflow_status TEXT NOT NULL,
                approval_status TEXT NOT NULL,
                iteration_count INTEGER NOT NULL,
                actions_count INTEGER NOT NULL,
                simulated_uplift_inr REAL NOT NULL,
                summary_text TEXT NOT NULL
            )
            """
        )


def record_run_state(
    thread_id: str,
    state: WorkflowState,
    db_path: str = DEFAULT_DB_PATH,
) -> None:
    """Record or update a workflow run entry from current workflow state."""
    conn = _get_connection(db_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    w_status = state.get("workflow_status", "initialized")
    a_status = state.get("approval_status", "pending")
    iter_count = state.get("iteration_count", 0)
    approved_acts = state.get("approved_actions", [])
    proposed_acts = state.get("proposed_actions", [])
    exec_acts = state.get("execution_results", [])
    actions_count = len(exec_acts) or len(approved_acts) or len(proposed_acts)

    measured = state.get("measured_outcomes", {})
    uplift = float(measured.get("total_simulated_revenue_uplift_inr", 0.0))

    learning = state.get("learning_summary", {})
    summary = learning.get("decision_reason") or (
        f"Workflow at status '{w_status}' (Approval: {a_status})"
    )

    with conn:
        # Check if row already exists
        cursor = conn.execute(
            "SELECT created_at FROM workflow_run_history WHERE thread_id = ?",
            (thread_id,),
        )
        row = cursor.fetchone()
        created_at = row["created_at"] if row else now_str

        conn.execute(
            """
            INSERT INTO workflow_run_history (
                thread_id, created_at, updated_at, workflow_status,
                approval_status, iteration_count, actions_count,
                simulated_uplift_inr, summary_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                updated_at = excluded.updated_at,
                workflow_status = excluded.workflow_status,
                approval_status = excluded.approval_status,
                iteration_count = excluded.iteration_count,
                actions_count = excluded.actions_count,
                simulated_uplift_inr = excluded.simulated_uplift_inr,
                summary_text = excluded.summary_text
            """,
            (
                thread_id,
                created_at,
                now_str,
                w_status,
                a_status,
                iter_count,
                actions_count,
                uplift,
                summary,
            ),
        )


def list_all_runs(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve all historical workflow runs ordered by latest update time."""
    conn = _get_connection(db_path)
    with conn:
        cursor = conn.execute(
            """
            SELECT thread_id, created_at, updated_at, workflow_status,
                   approval_status, iteration_count, actions_count,
                   simulated_uplift_inr, summary_text
            FROM workflow_run_history
            ORDER BY updated_at DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_run(thread_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve metadata for a specific thread ID."""
    conn = _get_connection(db_path)
    with conn:
        cursor = conn.execute(
            """
            SELECT thread_id, created_at, updated_at, workflow_status,
                   approval_status, iteration_count, actions_count,
                   simulated_uplift_inr, summary_text
            FROM workflow_run_history
            WHERE thread_id = ?
            """,
            (thread_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
