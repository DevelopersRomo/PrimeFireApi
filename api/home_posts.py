import contextlib
import os
from itertools import starmap
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_module_permission,
)
from bd.dependencies import get_db
from core.datetime_utils import utcnow
from core.file_storage import MIB, attachment_response, confine_to, detect_content_type, read_upload
from models.employees import Employees
from models.home_posts import HomePost
from schemas.home_posts import HomePostRead, HomePostWrite, PostStatus, PostType
from schemas.pagination import PaginatedResponse
from services.home_posts import post_status, status_filter

load_dotenv()

if os.getenv("ENVIRONMENT", "local").lower() == "prod":
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/home/home/uploads")) / "home_posts"
else:
    from core.config import settings

    UPLOAD_DIR = Path(__file__).resolve().parents[1] / settings.UPLOAD_DIR / "home_posts"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api/v1", tags=["home_posts"])

MAX_COVER_BYTES = 5 * MIB
COVER_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _author_name(author: Employees | None) -> str | None:
    if author is None:
        return None
    return author.display_name or " ".join(filter(None, [author.first_name, author.last_name])) or author.email


def _to_read(post: HomePost, author: Employees | None) -> HomePostRead:
    return HomePostRead(
        **post.model_dump(exclude={"cover_path", "cover_content_type", "is_active"}),
        author_name=_author_name(author),
        has_cover=bool(post.cover_path),
        status=post_status(post, utcnow()),
    )


def _select_with_author():
    return select(HomePost, Employees).outerjoin(Employees, Employees.employee_id == HomePost.created_by)


def _read_post(db: Session, post: HomePost) -> HomePostRead:
    return _to_read(post, db.get(Employees, post.created_by) if post.created_by else None)


def _can_view_all(user_permissions: dict) -> bool:
    return any(
        perm.get("module_key") == "home_posts" and perm.get("permissions", {}).get("can_view")
        for perm in user_permissions.get("permissions", [])
    )


def _get_active_or_404(db: Session, post_id: int) -> HomePost:
    post = db.get(HomePost, post_id)
    if not post or not post.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def _get_readable_or_404(db: Session, post_id: int, user_permissions: dict) -> HomePost:
    """Feed-visible posts are readable by anyone; drafts and the rest need home_posts.can_view."""
    post = _get_active_or_404(db, post_id)
    if post_status(post, utcnow()) != "published" and not _can_view_all(user_permissions):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


def _cover_file(post: HomePost) -> Path | None:
    return confine_to(UPLOAD_DIR, post.cover_path) if post.cover_path else None


def _remove_cover_file(post: HomePost) -> None:
    path = _cover_file(post)
    if path:
        with contextlib.suppress(OSError):
            path.unlink()


def _apply_payload(post: HomePost, payload: HomePostWrite) -> None:
    for field, value in payload.model_dump().items():
        setattr(post, field, value)
    post.updated_at = utcnow()


def _paginate(db: Session, filters: list, order_by: tuple, skip: int, limit: int) -> PaginatedResponse[HomePostRead]:
    rows = db.exec(_select_with_author().where(*filters).order_by(*order_by).offset(skip).limit(limit)).all()
    items = list(starmap(_to_read, rows))
    total = db.exec(select(func.count()).select_from(HomePost).where(*filters)).one()
    return PaginatedResponse[HomePostRead](
        items=items, total=total, skip=skip, limit=limit, has_more=skip + len(items) < total
    )


# Declared before /home-posts/{post_id} so "feed" is never parsed as an id.
@router.get("/home-posts/feed", response_model=PaginatedResponse[HomePostRead])
def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    post_type: PostType | None = None,
    db: Session = Depends(get_db),
    _employee=Depends(get_current_employee),
):
    filters = [HomePost.is_active, status_filter("published", utcnow())]
    if post_type:
        filters.append(HomePost.post_type == post_type)
    order_by = (HomePost.is_pinned.desc(), HomePost.published_at.desc(), HomePost.post_id.desc())
    return _paginate(db, filters, order_by, skip, limit)


@router.get("/home-posts", response_model=list[HomePostRead] | PaginatedResponse[HomePostRead])
def list_posts(
    search: str | None = None,
    post_type: PostType | None = None,
    status_: PostStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_view")),
):
    filters = [HomePost.is_active]
    if search and search.strip():
        filters.append(HomePost.title.ilike(f"%{search.strip()}%"))
    if post_type:
        filters.append(HomePost.post_type == post_type)
    if status_:
        filters.append(status_filter(status_, utcnow()))
    order_by = (
        HomePost.is_pinned.desc(),
        func.coalesce(HomePost.published_at, HomePost.created_at).desc(),
        HomePost.post_id.desc(),
    )
    page = _paginate(db, filters, order_by, skip, limit)
    return page if with_meta else page.items


@router.get("/home-posts/{post_id}", response_model=HomePostRead)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    return _read_post(db, _get_readable_or_404(db, post_id, user_permissions))


@router.post("/home-posts", response_model=HomePostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: HomePostWrite,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_create")),
    current_employee: Employees = Depends(get_current_employee),
):
    post = HomePost(title="", post_type="", body_html="", created_by=current_employee.employee_id)
    _apply_payload(post, payload)
    db.add(post)
    db.commit()
    db.refresh(post)
    return _read_post(db, post)


@router.put("/home-posts/{post_id}", response_model=HomePostRead)
def update_post(
    post_id: int,
    payload: HomePostWrite,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_edit")),
):
    post = _get_active_or_404(db, post_id)
    _apply_payload(post, payload)
    db.add(post)
    db.commit()
    db.refresh(post)
    return _read_post(db, post)


@router.delete("/home-posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_delete")),
):
    post = _get_active_or_404(db, post_id)
    post.is_active = False
    post.updated_at = utcnow()
    db.add(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/home-posts/{post_id}/cover", response_model=HomePostRead)
def upload_cover(
    post_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_edit")),
):
    post = _get_active_or_404(db, post_id)
    content = read_upload(file, MAX_COVER_BYTES)

    post_dir = UPLOAD_DIR / str(post_id)
    post_dir.mkdir(parents=True, exist_ok=True)
    stored = post_dir / uuid4().hex
    stored.write_bytes(content)
    content_type = detect_content_type(stored)
    if content_type not in COVER_EXTENSIONS:
        stored.unlink()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Cover must be a JPEG, PNG or WEBP image"
        )
    stored = stored.rename(stored.with_suffix(COVER_EXTENSIONS[content_type]))

    _remove_cover_file(post)
    post.cover_path = stored.relative_to(UPLOAD_DIR).as_posix()
    post.cover_content_type = content_type
    post.updated_at = utcnow()
    db.add(post)
    db.commit()
    db.refresh(post)
    return _read_post(db, post)


@router.delete("/home-posts/{post_id}/cover", status_code=status.HTTP_204_NO_CONTENT)
def delete_cover(
    post_id: int,
    db: Session = Depends(get_db),
    _perm=Depends(require_module_permission("home_posts", "can_edit")),
):
    post = _get_active_or_404(db, post_id)
    _remove_cover_file(post)
    post.cover_path = None
    post.cover_content_type = None
    post.updated_at = utcnow()
    db.add(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/home-posts/{post_id}/cover")
def get_cover(
    post_id: int,
    db: Session = Depends(get_db),
    user_permissions: dict = Depends(get_current_employee_with_permissions),
):
    path = _cover_file(_get_readable_or_404(db, post_id, user_permissions))
    if not path or not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cover not found")
    return attachment_response(path, path.name)
