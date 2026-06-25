"""Plane Plus MCP Server — exposes the Plane Plus SDK as MCP tools.

Configuration via environment variables:
    PLANE_BASE_URL       — e.g. https://plane.example.com
    PLANE_API_KEY        — API key for the target workspace
    PLANE_WORKSPACE_SLUG — e.g. my-workspace
"""

from __future__ import annotations

import json
import os
import traceback

from mcp.server.fastmcp import FastMCP

from plane_sdk import PlaneClient

# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

server = FastMCP(
    "Plane",
    instructions="Manage projects, work items, modules, cycles, and pages in Plane.",
)

_client: PlaneClient | None = None


def _get_client() -> PlaneClient:
    global _client
    if _client is None:
        base_url = os.environ.get("PLANE_BASE_URL", "")
        api_key = os.environ.get("PLANE_API_KEY", "")
        workspace = os.environ.get("PLANE_WORKSPACE_SLUG", "")
        if not all([base_url, api_key, workspace]):
            raise RuntimeError(
                "Missing env vars. Set PLANE_BASE_URL, PLANE_API_KEY, PLANE_WORKSPACE_SLUG"
            )
        _client = PlaneClient(base_url=base_url, api_key=api_key, workspace_slug=workspace)
    return _client


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


def _safe(fn):
    """Wrap a tool handler to catch exceptions and return readable errors."""
    try:
        return _json(fn())
    except Exception:
        return f"Error: {traceback.format_exc()}"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


@server.tool()
def get_me() -> str:
    """Get the authenticated user info."""
    return _safe(lambda: _get_client().get_me())


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


@server.tool()
def list_projects(member_only: bool = True) -> str:
    """List projects in the workspace. Default: only projects where user is a member. Set member_only=False to see all."""
    return _safe(lambda: _get_client().list_projects(member_only=member_only))


@server.tool()
def create_project(name: str, identifier: str, description: str = "", network: int = 2) -> str:
    """Create a new project. identifier must be 1-5 uppercase chars."""
    return _safe(lambda: _get_client().create_project(
        name=name, identifier=identifier, description=description, network=network,
    ))


@server.tool()
def retrieve_project(project_id: str) -> str:
    """Get project details."""
    return _safe(lambda: _get_client().get_project(project_id))


@server.tool()
def update_project(project_id: str, name: str = "", description: str = "") -> str:
    """Update project fields."""
    data = {k: v for k, v in {"name": name, "description": description}.items() if v}
    return _safe(lambda: _get_client().update_project(project_id, **data))


@server.tool()
def delete_project(project_id: str) -> str:
    """Delete a project."""
    return _safe(lambda: _get_client().delete_project(project_id) or "Deleted")


# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------


@server.tool()
def list_states(project_id: str) -> str:
    """List all states in a project."""
    return _safe(lambda: _get_client().list_states(project_id))


@server.tool()
def create_state(project_id: str, name: str, color: str, group: str) -> str:
    """Create a state. group: backlog, unstarted, started, completed, cancelled."""
    return _safe(lambda: _get_client().create_state(project_id, name=name, color=color, group=group))


@server.tool()
def update_state(project_id: str, state_id: str, name: str = "", color: str = "") -> str:
    """Update a state."""
    data = {k: v for k, v in {"name": name, "color": color}.items() if v}
    return _safe(lambda: _get_client().update_state(project_id, state_id, **data))


@server.tool()
def delete_state(project_id: str, state_id: str) -> str:
    """Delete a state."""
    return _safe(lambda: _get_client().delete_state(project_id, state_id) or "Deleted")


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------


@server.tool()
def list_labels(project_id: str) -> str:
    """List all labels in a project."""
    return _safe(lambda: _get_client().list_labels(project_id))


@server.tool()
def create_label(project_id: str, name: str, color: str = "#6b7280") -> str:
    """Create a label."""
    return _safe(lambda: _get_client().create_label(project_id, name=name, color=color))


@server.tool()
def update_label(project_id: str, label_id: str, name: str = "", color: str = "") -> str:
    """Update a label."""
    data = {k: v for k, v in {"name": name, "color": color}.items() if v}
    return _safe(lambda: _get_client().update_label(project_id, label_id, **data))


@server.tool()
def delete_label(project_id: str, label_id: str) -> str:
    """Delete a label."""
    return _safe(lambda: _get_client().delete_label(project_id, label_id) or "Deleted")


# ---------------------------------------------------------------------------
# Work Items
# ---------------------------------------------------------------------------


@server.tool()
def list_work_items(project_id: str) -> str:
    """List work items in a project."""
    return _safe(lambda: _get_client().list_work_items(project_id))


@server.tool()
def create_work_item(
    project_id: str,
    name: str,
    description_html: str = "",
    priority: str = "none",
    state_id: str = "",
    label_ids: list[str] | None = None,
    assignee_ids: list[str] | None = None,
    parent_id: str = "",
) -> str:
    """Create a work item. priority: urgent, high, medium, low, none. Pass parent_id to create a sub-work-item under an existing parent."""
    data: dict = {"name": name, "priority": priority}
    if description_html:
        data["description_html"] = description_html
    if state_id:
        data["state"] = state_id
    if label_ids:
        data["labels"] = label_ids
    if assignee_ids:
        data["assignees"] = assignee_ids
    if parent_id:
        data["parent"] = parent_id
    return _safe(lambda: _get_client().create_work_item(project_id, **data))


@server.tool()
def retrieve_work_item(project_id: str, work_item_id: str) -> str:
    """Get work item details by project UUID and work item UUID."""
    return _safe(lambda: _get_client().get_work_item(project_id, work_item_id))


@server.tool()
def retrieve_work_item_by_identifier(identifier: str) -> str:
    """Get a work item by its human-readable identifier (e.g. 'WEB-123' or 'INFRA-42').
    Resolves the project automatically — no project_id needed.
    Returns full work item details including project_id for use in subsequent calls."""
    return _safe(lambda: _get_client().get_work_item_by_identifier(identifier))


@server.tool()
def update_work_item(
    project_id: str,
    work_item_id: str,
    name: str = "",
    description_html: str = "",
    priority: str = "",
    state_id: str = "",
    label_ids: list[str] | None = None,
    assignee_ids: list[str] | None = None,
    parent_id: str | None = None,
) -> str:
    """Update a work item. label_ids and assignee_ids are REPLACE (full list, not append). Pass parent_id as a UUID to re-parent, or an empty string to clear (un-parent)."""
    data = {}
    if name:
        data["name"] = name
    if description_html:
        data["description_html"] = description_html
    if priority:
        data["priority"] = priority
    if label_ids is not None:
        data["labels"] = label_ids
    if assignee_ids is not None:
        data["assignees"] = assignee_ids
    if state_id:
        data["state"] = state_id
    if parent_id is not None:
        # Empty string clears the parent; non-empty sets it.
        data["parent"] = parent_id or None
    return _safe(lambda: _get_client().update_work_item(project_id, work_item_id, **data))


@server.tool()
def delete_work_item(project_id: str, work_item_id: str) -> str:
    """Delete a work item."""
    return _safe(lambda: _get_client().delete_work_item(project_id, work_item_id) or "Deleted")


# ---------------------------------------------------------------------------
# Epics
# ---------------------------------------------------------------------------


@server.tool()
def list_epics(project_id: str) -> str:
    """List epics in a project. Epics are high-level issues that group work items."""
    return _safe(lambda: _get_client().list_epics(project_id))


@server.tool()
def create_epic(
    project_id: str,
    name: str,
    description_html: str = "",
    priority: str = "none",
    state_id: str = "",
    label_ids: list[str] | None = None,
    assignee_ids: list[str] | None = None,
) -> str:
    """Create an epic. The epic issue type is set automatically. priority: urgent, high, medium, low, none."""
    data: dict = {"name": name, "priority": priority}
    if description_html:
        data["description_html"] = description_html
    if state_id:
        data["state"] = state_id
    if label_ids:
        data["labels"] = label_ids
    if assignee_ids:
        data["assignees"] = assignee_ids
    return _safe(lambda: _get_client().create_epic(project_id, **data))


@server.tool()
def retrieve_epic(project_id: str, epic_id: str) -> str:
    """Get epic details."""
    return _safe(lambda: _get_client().get_epic(project_id, epic_id))


@server.tool()
def update_epic(
    project_id: str,
    epic_id: str,
    name: str = "",
    description_html: str = "",
    priority: str = "",
    state_id: str = "",
    label_ids: list[str] | None = None,
    assignee_ids: list[str] | None = None,
) -> str:
    """Update an epic. label_ids and assignee_ids are REPLACE (full list, not append)."""
    data = {}
    if name:
        data["name"] = name
    if description_html:
        data["description_html"] = description_html
    if priority:
        data["priority"] = priority
    if label_ids is not None:
        data["labels"] = label_ids
    if assignee_ids is not None:
        data["assignees"] = assignee_ids
    if state_id:
        data["state"] = state_id
    return _safe(lambda: _get_client().update_epic(project_id, epic_id, **data))


@server.tool()
def delete_epic(project_id: str, epic_id: str) -> str:
    """Delete an epic."""
    return _safe(lambda: _get_client().delete_epic(project_id, epic_id) or "Deleted")


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------


@server.tool()
def list_work_item_comments(project_id: str, work_item_id: str) -> str:
    """List comments on a work item."""
    return _safe(lambda: _get_client().list_comments(project_id, work_item_id))


@server.tool()
def create_work_item_comment(project_id: str, work_item_id: str, comment_html: str) -> str:
    """Add a comment to a work item."""
    return _safe(lambda: _get_client().create_comment(project_id, work_item_id, comment_html=comment_html))


@server.tool()
def delete_work_item_comment(project_id: str, work_item_id: str, comment_id: str) -> str:
    """Delete a comment."""
    return _safe(lambda: _get_client().delete_comment(project_id, work_item_id, comment_id) or "Deleted")


@server.tool()
def update_work_item_comment(project_id: str, work_item_id: str, comment_id: str, comment_html: str) -> str:
    """Update a comment on a work item."""
    return _safe(lambda: _get_client().update_comment(project_id, work_item_id, comment_id, comment_html=comment_html))


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------


@server.tool()
def list_work_item_links(project_id: str, work_item_id: str) -> str:
    """List links on a work item."""
    return _safe(lambda: _get_client().list_links(project_id, work_item_id))


@server.tool()
def create_work_item_link(project_id: str, work_item_id: str, url: str, title: str = "") -> str:
    """Add a link to a work item."""
    kwargs = {"title": title} if title else {}
    return _safe(lambda: _get_client().create_link(project_id, work_item_id, url=url, **kwargs))


@server.tool()
def delete_work_item_link(project_id: str, work_item_id: str, link_id: str) -> str:
    """Delete a link."""
    return _safe(lambda: _get_client().delete_link(project_id, work_item_id, link_id) or "Deleted")


# ---------------------------------------------------------------------------
# Relations
# ---------------------------------------------------------------------------


@server.tool()
def list_work_item_relations(project_id: str, work_item_id: str) -> str:
    """List relations for a work item, grouped by type: blocking, blocked_by, duplicate, relates_to, start_before, start_after, finish_before, finish_after."""
    return _safe(lambda: _get_client().list_relations(project_id, work_item_id))


@server.tool()
def create_work_item_relation(
    project_id: str, work_item_id: str, relation_type: str, related_work_item_ids: list[str]
) -> str:
    """Create a relation between work items. relation_type: blocking, blocked_by, duplicate, relates_to, start_before, start_after, finish_before, finish_after."""
    return _safe(lambda: _get_client().create_relation(
        project_id, work_item_id, relation_type=relation_type, related_work_item_ids=related_work_item_ids,
    ))


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


@server.tool()
def list_work_item_activities(project_id: str, work_item_id: str) -> str:
    """List activity history for a work item."""
    return _safe(lambda: _get_client().list_activities(project_id, work_item_id))


# ---------------------------------------------------------------------------
# Modules
# ---------------------------------------------------------------------------


@server.tool()
def list_modules(project_id: str) -> str:
    """List all modules in a project."""
    return _safe(lambda: _get_client().list_modules(project_id))


@server.tool()
def create_module(project_id: str, name: str, description: str = "") -> str:
    """Create a module."""
    kwargs = {"description": description} if description else {}
    return _safe(lambda: _get_client().create_module(project_id, name=name, **kwargs))


@server.tool()
def retrieve_module(project_id: str, module_id: str) -> str:
    """Get module details."""
    return _safe(lambda: _get_client().get_module(project_id, module_id))


@server.tool()
def update_module(project_id: str, module_id: str, name: str = "", description: str = "") -> str:
    """Update a module."""
    data = {k: v for k, v in {"name": name, "description": description}.items() if v}
    return _safe(lambda: _get_client().update_module(project_id, module_id, **data))


@server.tool()
def delete_module(project_id: str, module_id: str) -> str:
    """Delete a module."""
    return _safe(lambda: _get_client().delete_module(project_id, module_id) or "Deleted")


@server.tool()
def list_module_work_items(project_id: str, module_id: str) -> str:
    """List work items in a module."""
    return _safe(lambda: _get_client().list_module_work_items(project_id, module_id))


@server.tool()
def add_work_items_to_module(project_id: str, module_id: str, work_item_ids: list[str]) -> str:
    """Add work items to a module."""
    return _safe(lambda: _get_client().add_work_items_to_module(project_id, module_id, work_item_ids))


@server.tool()
def remove_work_item_from_module(project_id: str, module_id: str, work_item_id: str) -> str:
    """Remove a work item from a module."""
    return _safe(lambda: _get_client().remove_work_item_from_module(project_id, module_id, work_item_id) or "Removed")


# ---------------------------------------------------------------------------
# Cycles
# ---------------------------------------------------------------------------


@server.tool()
def list_cycles(project_id: str) -> str:
    """List all cycles in a project."""
    return _safe(lambda: _get_client().list_cycles(project_id))


@server.tool()
def create_cycle(
    project_id: str, name: str, start_date: str = "", end_date: str = "", description: str = ""
) -> str:
    """Create a cycle. Dates in YYYY-MM-DD format."""
    kwargs: dict = {}
    if start_date:
        kwargs["start_date"] = start_date
    if end_date:
        kwargs["end_date"] = end_date
    if description:
        kwargs["description"] = description
    return _safe(lambda: _get_client().create_cycle(project_id, name=name, **kwargs))


@server.tool()
def retrieve_cycle(project_id: str, cycle_id: str) -> str:
    """Get cycle details."""
    return _safe(lambda: _get_client().get_cycle(project_id, cycle_id))


@server.tool()
def update_cycle(project_id: str, cycle_id: str, name: str = "", start_date: str = "", end_date: str = "") -> str:
    """Update a cycle."""
    data = {k: v for k, v in {"name": name, "start_date": start_date, "end_date": end_date}.items() if v}
    return _safe(lambda: _get_client().update_cycle(project_id, cycle_id, **data))


@server.tool()
def delete_cycle(project_id: str, cycle_id: str) -> str:
    """Delete a cycle."""
    return _safe(lambda: _get_client().delete_cycle(project_id, cycle_id) or "Deleted")


@server.tool()
def list_cycle_work_items(project_id: str, cycle_id: str) -> str:
    """List work items in a cycle."""
    return _safe(lambda: _get_client().list_cycle_work_items(project_id, cycle_id))


@server.tool()
def add_work_items_to_cycle(project_id: str, cycle_id: str, work_item_ids: list[str]) -> str:
    """Add work items to a cycle."""
    return _safe(lambda: _get_client().add_work_items_to_cycle(project_id, cycle_id, work_item_ids))


@server.tool()
def remove_work_item_from_cycle(project_id: str, cycle_id: str, work_item_id: str) -> str:
    """Remove a work item from a cycle."""
    return _safe(lambda: _get_client().remove_work_item_from_cycle(project_id, cycle_id, work_item_id) or "Removed")


@server.tool()
def transfer_cycle_work_items(project_id: str, cycle_id: str, new_cycle_id: str) -> str:
    """Transfer all work items from one cycle to another."""
    return _safe(lambda: _get_client().transfer_cycle_work_items(project_id, cycle_id, new_cycle_id=new_cycle_id))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@server.tool()
def list_pages(project_id: str) -> str:
    """List pages in a project."""
    return _safe(lambda: _get_client().list_pages(project_id))


@server.tool()
def create_project_page(project_id: str, name: str, description_html: str = "") -> str:
    """Create a page in a project."""
    kwargs = {"description_html": description_html} if description_html else {}
    return _safe(lambda: _get_client().create_page(project_id, name=name, **kwargs))


@server.tool()
def retrieve_project_page(project_id: str, page_id: str, response_format: str = "html") -> str:
    """Get page details. Set response_format="markdown" to get description_markdown in addition to description_html."""
    return _safe(lambda: _get_client().get_page(project_id, page_id, response_format=response_format))


@server.tool()
def update_project_page(project_id: str, page_id: str, name: str = "") -> str:
    """Update page metadata (name, etc.)."""
    data = {k: v for k, v in {"name": name}.items() if v}
    return _safe(lambda: _get_client().update_page(project_id, page_id, **data))


@server.tool()
def update_page_content(project_id: str, page_id: str, content_html: str, content_format: str = "html") -> str:
    """Replace the full page content (body). Use HTML tags for formatting, or set content_format="markdown" to write in markdown (converted to HTML server-side)."""
    return _safe(lambda: _get_client().update_page_content(project_id, page_id, content_html, content_format=content_format))


# ---------------------------------------------------------------------------
# Workspace Pages (wiki)
# ---------------------------------------------------------------------------


@server.tool()
def list_workspace_pages() -> str:
    """List all workspace-level pages (wiki pages not tied to a project)."""
    return _safe(lambda: _get_client().list_workspace_pages())


@server.tool()
def create_workspace_page(name: str, description_html: str = "") -> str:
    """Create a workspace-level page (wiki). Not tied to any project."""
    kwargs = {"description_html": description_html} if description_html else {}
    return _safe(lambda: _get_client().create_workspace_page(name=name, **kwargs))


@server.tool()
def retrieve_workspace_page(page_id: str, response_format: str = "html") -> str:
    """Get workspace page details. Set response_format="markdown" to get description_markdown in addition to description_html."""
    return _safe(lambda: _get_client().get_workspace_page(page_id, response_format=response_format))


@server.tool()
def update_workspace_page(page_id: str, name: str = "") -> str:
    """Update workspace page metadata (name, etc.)."""
    data = {k: v for k, v in {"name": name}.items() if v}
    return _safe(lambda: _get_client().update_workspace_page(page_id, **data))


@server.tool()
def delete_workspace_page(page_id: str) -> str:
    """Delete a workspace page."""
    return _safe(lambda: _get_client().delete_workspace_page(page_id) or "Deleted")


# ---------------------------------------------------------------------------
# Intake (triage)
# ---------------------------------------------------------------------------


@server.tool()
def list_intake_work_items(project_id: str) -> str:
    """List intake (triage) items in a project."""
    return _safe(lambda: _get_client().list_intake_work_items(project_id))


@server.tool()
def create_intake_work_item(
    project_id: str,
    name: str,
    description_html: str = "",
    priority: str = "none",
) -> str:
    """Create an intake item (idea/request for triage). Goes to intake queue, not backlog."""
    data: dict = {"name": name, "priority": priority}
    if description_html:
        data["description_html"] = description_html
    return _safe(lambda: _get_client().create_intake_work_item(project_id, **data))


@server.tool()
def retrieve_intake_work_item(project_id: str, intake_id: str) -> str:
    """Get intake item details."""
    return _safe(lambda: _get_client().get_intake_work_item(project_id, intake_id))


@server.tool()
def update_intake_work_item(project_id: str, intake_id: str, name: str = "", priority: str = "", state_id: str = "") -> str:
    """Update an intake item."""
    data = {k: v for k, v in {"name": name, "priority": priority, "state": state_id}.items() if v}
    return _safe(lambda: _get_client().update_intake_work_item(project_id, intake_id, **data))


@server.tool()
def delete_intake_work_item(project_id: str, intake_id: str) -> str:
    """Delete an intake item."""
    return _safe(lambda: _get_client().delete_intake_work_item(project_id, intake_id) or "Deleted")


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------


@server.tool()
def get_workspace_members() -> str:
    """List all workspace members."""
    return _safe(lambda: _get_client().list_workspace_members())


@server.tool()
def get_project_members(project_id: str) -> str:
    """List all members of a project."""
    return _safe(lambda: _get_client().list_project_members(project_id))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
