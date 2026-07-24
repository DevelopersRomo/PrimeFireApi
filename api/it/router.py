from fastapi import APIRouter

from api.it import (
    catalog,
    categories,
    documents,
    email_templates,
    licenses,
    quotations,
    templates,
)

router = APIRouter(prefix="/it")

router.include_router(
    categories.router,
    prefix="/catalog/categories",
    tags=["IT Catalog Categories"],
)
router.include_router(
    catalog.router,
    prefix="/catalog/items",
    tags=["IT Catalog"],
)
router.include_router(
    licenses.router,
    prefix="/licenses",
    tags=["IT Licenses"],
)
router.include_router(
    quotations.router,
    prefix="/quotations",
    tags=["IT Quotations"],
)
router.include_router(
    documents.router,
    prefix="/documents",
    tags=["IT Documents"],
)
router.include_router(
    templates.router,
    prefix="/templates",
    tags=["IT PDF Templates"],
)
router.include_router(
    email_templates.router,
    prefix="/email-templates",
    tags=["IT Email Templates"],
)
