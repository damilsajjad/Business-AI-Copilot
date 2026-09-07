"""Supabase client initialization.

Uses the service role key for backend admin operations.
Provides seamless in-memory database fallback when live Supabase credentials
are not configured or when running in local development mode.
"""

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any
from uuid import uuid4

from supabase import Client, create_client

from app.core.config import settings


class SupabaseClientError(Exception):
    """Raised when Supabase client cannot be initialized."""


class MockQueryResult:
    """Mock query result matching Supabase API response."""

    def __init__(self, data: Any = None):
        self.data = data


class MockTableQuery:
    """Mock Supabase table query builder supporting filtering, joins, and mutations."""

    def __init__(self, db: dict[str, list[dict[str, Any]]], table_name: str):
        self.db = db
        self.table_name = table_name
        self._action = "select"
        self._select_cols = "*"
        self._insert_data: list[dict[str, Any]] = []
        self._update_data: dict[str, Any] = {}
        self._on_conflict: str | None = None
        self._filters: list[tuple[str, Any]] = []
        self._order_by: tuple[str, bool] | None = None
        self._limit: int | None = None
        self._is_single: bool = False

        if self.table_name not in self.db:
            self.db[self.table_name] = []

    def select(self, columns: str = "*") -> "MockTableQuery":
        self._action = "select"
        self._select_cols = columns
        return self

    def single(self) -> "MockTableQuery":
        self._is_single = True
        return self

    def insert(self, data: dict[str, Any] | list[dict[str, Any]]) -> "MockTableQuery":
        self._action = "insert"
        if isinstance(data, list):
            self._insert_data = data
        else:
            self._insert_data = [data]
        return self

    def upsert(self, data: dict[str, Any] | list[dict[str, Any]], on_conflict: str | None = None) -> "MockTableQuery":
        self._action = "upsert"
        self._on_conflict = on_conflict
        if isinstance(data, list):
            self._insert_data = data
        else:
            self._insert_data = [data]
        return self

    def update(self, data: dict[str, Any]) -> "MockTableQuery":
        self._action = "update"
        self._update_data = data
        return self

    def delete(self) -> "MockTableQuery":
        self._action = "delete"
        return self

    def eq(self, column: str, value: Any) -> "MockTableQuery":
        self._filters.append((column, str(value)))
        return self

    def order(self, column: str, desc: bool = False) -> "MockTableQuery":
        self._order_by = (column, desc)
        return self

    def limit(self, count: int) -> "MockTableQuery":
        self._limit = count
        return self

    def execute(self) -> MockQueryResult:
        table = self.db[self.table_name]

        if self._action == "insert":
            inserted = []
            now = datetime.now(timezone.utc).isoformat()
            for row in self._insert_data:
                row_copy = dict(row)
                if "id" not in row_copy:
                    row_copy["id"] = str(uuid4())
                if "created_at" not in row_copy:
                    row_copy["created_at"] = now
                if "updated_at" not in row_copy:
                    row_copy["updated_at"] = now
                table.append(row_copy)
                inserted.append(row_copy)
            return MockQueryResult(inserted[0] if self._is_single and inserted else inserted)

        elif self._action == "upsert":
            upserted = []
            now = datetime.now(timezone.utc).isoformat()
            conflict_cols = [c.strip() for c in (self._on_conflict or "id").split(",")]
            for row in self._insert_data:
                row_copy = dict(row)
                if "id" not in row_copy:
                    row_copy["id"] = str(uuid4())
                if "created_at" not in row_copy:
                    row_copy["created_at"] = now
                row_copy["updated_at"] = now

                existing_idx = None
                for i, r in enumerate(table):
                    if all(
                        str(r.get(col, "")) == str(row_copy.get(col, ""))
                        for col in conflict_cols
                        if col in row_copy
                    ):
                        existing_idx = i
                        break

                if existing_idx is not None:
                    table[existing_idx].update(row_copy)
                    upserted.append(dict(table[existing_idx]))
                else:
                    table.append(row_copy)
                    upserted.append(row_copy)
            return MockQueryResult(upserted[0] if self._is_single and upserted else upserted)

        elif self._action == "update":
            updated = []
            now = datetime.now(timezone.utc).isoformat()
            for row in table:
                if self._matches_filters(row):
                    row.update(self._update_data)
                    row["updated_at"] = now
                    updated.append(dict(row))
            return MockQueryResult(updated[0] if self._is_single and updated else updated)

        elif self._action == "delete":
            deleted = []
            remaining = []
            for row in table:
                if self._matches_filters(row):
                    deleted.append(dict(row))
                else:
                    remaining.append(row)
            self.db[self.table_name] = remaining
            return MockQueryResult(deleted[0] if self._is_single and deleted else deleted)

        else:  # select
            results = [dict(row) for row in table if self._matches_filters(row)]

            # Handle order
            if self._order_by:
                col, desc = self._order_by
                results.sort(key=lambda r: str(r.get(col, "")), reverse=desc)

            # Handle limit
            if self._limit is not None:
                results = results[: self._limit]

            # Handle foreign relation join: role, businesses(*)
            if self.table_name == "business_memberships" and "businesses(*)" in self._select_cols:
                businesses_table = self.db.get("businesses", [])
                joined_results = []
                for row in results:
                    biz_id = str(row.get("business_id"))
                    biz = next(
                        (b for b in businesses_table if str(b.get("id")) == biz_id),
                        None,
                    )
                    joined_results.append(
                        {
                            "id": row.get("id"),
                            "role": row.get("role", "owner"),
                            "business_id": biz_id,
                            "businesses": dict(biz) if biz else {},
                        }
                    )
                if self._is_single:
                    return MockQueryResult(joined_results[0] if joined_results else None)
                return MockQueryResult(joined_results)

            if self._is_single:
                return MockQueryResult(results[0] if results else None)

            return MockQueryResult(results)

    def _matches_filters(self, row: dict[str, Any]) -> bool:
        for col, val in self._filters:
            if str(row.get(col)) != str(val):
                return False
        return True


class MockUser:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email


class MockUserResponse:
    def __init__(self, user: MockUser):
        self.user = user


class MockAuthAdmin:
    def __init__(self, db: dict[str, list[dict[str, Any]]]):
        self.db = db

    def create_user(self, attributes: dict[str, Any]) -> MockUserResponse:
        email = attributes.get("email", "")
        for u in self.db.get("profiles", []):
            if u.get("email") == email:
                raise Exception("A user with this email address has already been registered")
        uid = str(uuid4())
        profile = {
            "id": uid,
            "email": email,
            "full_name": attributes.get("user_metadata", {}).get("full_name", ""),
        }
        if "profiles" not in self.db:
            self.db["profiles"] = []
        self.db["profiles"].append(profile)
        return MockUserResponse(MockUser(uid, email))


class MockAuth:
    def __init__(self, db: dict[str, list[dict[str, Any]]]):
        self.admin = MockAuthAdmin(db)


class InMemorySupabaseClient:
    """In-memory Supabase client replacement for development and test execution."""

    def __init__(self):
        self.db: dict[str, list[dict[str, Any]]] = {
            "businesses": [],
            "business_memberships": [],
            "file_uploads": [],
            "schema_mappings": [],
            "action_items": [],
            "analytics_snapshots": [],
            "ai_insights": [],
            "scheduled_reports": [],
            "profiles": [],
        }
        self.auth = MockAuth(self.db)

    def table(self, table_name: str) -> MockTableQuery:
        return MockTableQuery(self.db, table_name)


# Global in-memory singleton for development fallback
_in_memory_client: InMemorySupabaseClient | None = None


def _get_in_memory_client() -> InMemorySupabaseClient:
    global _in_memory_client
    if _in_memory_client is None:
        _in_memory_client = InMemorySupabaseClient()
    return _in_memory_client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get or create the Supabase client singleton.

    Uses the service role key for full backend access.
    Falls back gracefully to an in-memory client if live credentials are not configured.
    """
    url = settings.supabase_url
    key = settings.supabase_service_role_key

    is_configured = (
        bool(url)
        and bool(key)
        and not url.startswith("https://placeholder")
        and not key.startswith("your-")
        and not key.startswith("placeholder")
    )

    if not is_configured:
        return _get_in_memory_client()  # type: ignore[return-value]

    try:
        return create_client(url, key)
    except Exception:
        return _get_in_memory_client()  # type: ignore[return-value]
