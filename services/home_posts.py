"""Home posts: body sanitization and the date-derived status."""

import html
from datetime import datetime

import nh3
from sqlalchemy import and_, or_

from models.home_posts import HomePost

STATUSES = ("draft", "scheduled", "published", "expired")

_QUILL_CLASSES = {
    "ql-align-center",
    "ql-align-right",
    "ql-align-justify",
    *(f"ql-indent-{level}" for level in range(1, 9)),
}

_CLEAN_OPTIONS = {
    "tags": {"p", "br", "strong", "b", "em", "i", "u", "s", "h1", "h2", "h3", "ul", "ol", "li", "a", "blockquote"},
    "attributes": {"a": {"href"}, "li": {"data-list"}},
    "url_schemes": {"http", "https", "mailto"},
    "link_rel": "noopener noreferrer",
    "set_tag_attribute_values": {"a": {"target": "_blank"}},
    "allowed_classes": dict.fromkeys(("p", "h1", "h2", "h3", "li"), _QUILL_CLASSES),
}


def sanitize_body_html(raw: str) -> str:
    """Keep the Quill formatting subset; raise ValueError when no text survives."""
    cleaned = nh3.clean(raw, **_CLEAN_OPTIONS)
    if not html.unescape(nh3.clean(cleaned, tags=set())).strip():
        raise ValueError("Body must contain text")
    return cleaned


def post_status(post: HomePost, now: datetime) -> str:
    if post.published_at is None:
        return "draft"
    if post.published_at > now:
        return "scheduled"
    if post.expires_at is not None and post.expires_at <= now:
        return "expired"
    return "published"


def status_filter(status: str, now: datetime):
    """SQL condition matching post_status() for one status."""
    live = and_(HomePost.published_at.is_not(None), HomePost.published_at <= now)
    return {
        "draft": HomePost.published_at.is_(None),
        "scheduled": HomePost.published_at > now,
        "expired": and_(live, HomePost.expires_at <= now),
        "published": and_(live, or_(HomePost.expires_at.is_(None), HomePost.expires_at > now)),
    }[status]
