from datetime import datetime, timezone

from database import get_connection, initialize_database


class ContentManager:
    def __init__(self):
        initialize_database()

    def create_content(self, title, body, platform="blogger"):
        if not title or not body:
            return None
        created_at = datetime.now(timezone.utc).isoformat()
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO content (title, body, platform, status, created_at) VALUES (?, ?, ?, 'draft', ?)",
                (title, body, platform, created_at),
            )
            row = connection.execute(
                "SELECT * FROM content WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def get_all_content(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM content ORDER BY id DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def get_content(self, content_id):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM content WHERE id = ?", (content_id,)
            ).fetchone()
            return dict(row) if row else None

    def publish_content(self, content_id):
        with get_connection() as connection:
            cursor = connection.execute(
                "UPDATE content SET status = 'ready_to_publish' WHERE id = ?",
                (content_id,),
            )
            if not cursor.rowcount:
                return None
            row = connection.execute(
                "SELECT * FROM content WHERE id = ?", (content_id,)
            ).fetchone()
            return dict(row)

    def mark_published(self, content_id, post=None):
        post = post or {}
        with get_connection() as connection:
            cursor = connection.execute(
                """UPDATE content SET status = 'published',
                   external_post_id = ?, external_url = ? WHERE id = ?""",
                (str(post.get("id")) if post.get("id") is not None else None,
                 post.get("url"), content_id),
            )
            if not cursor.rowcount:
                return None
            row = connection.execute(
                "SELECT * FROM content WHERE id = ?", (content_id,)
            ).fetchone()
            return dict(row)

    def delete_content(self, content_id):
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM content WHERE id = ?", (content_id,)
            )
            return cursor.rowcount > 0
