"""Work item (issue) operations."""

from __future__ import annotations
from typing import Any


class WorkItemsMixin:
    # -- work items ----------------------------------------------------------

    def list_work_items(self, project_id: str) -> dict:
        return self._get(self._project_url(project_id, "work-items/"))

    def create_work_item(self, project_id: str, *, name: str, **kwargs: Any) -> dict:
        return self._post(self._project_url(project_id, "work-items/"), {"name": name, **kwargs})

    def get_work_item(self, project_id: str, work_item_id: str) -> dict:
        return self._get(self._project_url(project_id, f"work-items/{work_item_id}/"))

    def get_work_item_by_identifier(self, identifier: str) -> dict:
        """Look up a work item by its human-readable identifier (e.g. 'WEB-123').

        Parses the project prefix, resolves the project UUID, then fetches the work
        item using the sequence_id filter. Returns the work item dict with
        'project_id' included for convenience so callers don't need a second lookup.

        Raises ValueError on a bad identifier format or when the item is not found.
        """
        parts = identifier.upper().rsplit("-", 1)
        if len(parts) != 2 or not parts[1].isdigit():
            raise ValueError(
                f"Invalid work item identifier: {identifier!r}. Expected format: PROJECT-123"
            )
        project_prefix, sequence_id = parts[0], int(parts[1])

        # Resolve project UUID from the human-readable prefix
        projects_data = self.list_projects(member_only=False)
        project_list = (
            projects_data if isinstance(projects_data, list)
            else projects_data.get("results", [])
        )
        project = next(
            (p for p in project_list if p.get("identifier") == project_prefix), None
        )
        if project is None:
            raise ValueError(f"Project '{project_prefix}' not found in workspace")
        project_id = project["id"]

        # Fetch work items filtered by sequence_id (Plane API query param)
        data = self._get(self._project_url(project_id, "work-items/"), sequence_id=sequence_id)
        items = data if isinstance(data, list) else data.get("results", [])
        if not items:
            raise ValueError(
                f"Work item '{identifier}' not found in project '{project_prefix}'"
            )
        return {"project_id": project_id, **items[0]}

    def update_work_item(self, project_id: str, work_item_id: str, **kwargs: Any) -> dict:
        return self._patch(self._project_url(project_id, f"work-items/{work_item_id}/"), kwargs)

    def delete_work_item(self, project_id: str, work_item_id: str) -> None:
        return self._delete(self._project_url(project_id, f"work-items/{work_item_id}/"))

    # -- comments ------------------------------------------------------------

    def list_comments(self, project_id: str, work_item_id: str) -> dict:
        return self._get(self._project_url(project_id, f"work-items/{work_item_id}/comments/"))

    def create_comment(self, project_id: str, work_item_id: str, *, comment_html: str, **kwargs: Any) -> dict:
        return self._post(
            self._project_url(project_id, f"work-items/{work_item_id}/comments/"),
            {"comment_html": comment_html, **kwargs},
        )

    def update_comment(self, project_id: str, work_item_id: str, comment_id: str, **kwargs: Any) -> dict:
        return self._patch(
            self._project_url(project_id, f"work-items/{work_item_id}/comments/{comment_id}/"), kwargs
        )

    def delete_comment(self, project_id: str, work_item_id: str, comment_id: str) -> None:
        return self._delete(self._project_url(project_id, f"work-items/{work_item_id}/comments/{comment_id}/"))

    # -- links ---------------------------------------------------------------

    def list_links(self, project_id: str, work_item_id: str) -> dict:
        return self._get(self._project_url(project_id, f"work-items/{work_item_id}/links/"))

    def create_link(self, project_id: str, work_item_id: str, *, url: str, **kwargs: Any) -> dict:
        return self._post(
            self._project_url(project_id, f"work-items/{work_item_id}/links/"),
            {"url": url, **kwargs},
        )

    def delete_link(self, project_id: str, work_item_id: str, link_id: str) -> None:
        return self._delete(self._project_url(project_id, f"work-items/{work_item_id}/links/{link_id}/"))

    # -- relations -----------------------------------------------------------

    def list_relations(self, project_id: str, work_item_id: str) -> dict:
        """List relations grouped by type: blocking, blocked_by, duplicate, relates_to, etc."""
        return self._get(self._project_url(project_id, f"work-items/{work_item_id}/relations/"))

    def create_relation(
        self, project_id: str, work_item_id: str, *, relation_type: str, related_work_item_ids: list[str]
    ) -> list:
        """Create relations. relation_type: blocking, blocked_by, duplicate, relates_to,
        start_before, start_after, finish_before, finish_after."""
        return self._post(
            self._project_url(project_id, f"work-items/{work_item_id}/relations/"),
            {"relation_type": relation_type, "issues": related_work_item_ids},
        )

    # -- activities ----------------------------------------------------------

    def list_activities(self, project_id: str, work_item_id: str) -> dict:
        return self._get(self._project_url(project_id, f"work-items/{work_item_id}/activities/"))
