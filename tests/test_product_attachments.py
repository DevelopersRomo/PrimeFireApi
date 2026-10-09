from models.products import ProductAttachments, Products


def test_product_attachment_create_requires_products_can_edit(
    client, auth_headers, db_session, permission_override, monkeypatch, tmp_path
):
    import api.product_attachments as attachments_api

    permission_override("products", set())
    monkeypatch.setattr(attachments_api, "UPLOAD_DIR", tmp_path / "uploads")
    product = Products(name="Attachment Permission Product", type="Product")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = client.post(
        f"/products/{product.id}/attachments",
        files={"file": ("image.png", b"image", "image/png")},
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_product_attachment_delete_requires_products_can_delete(
    client, auth_headers, db_session, permission_override, tmp_path
):
    permission_override("products", set())
    product = Products(name="Attachment Delete Product", type="Product")
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    stored_file = tmp_path / "product.png"
    stored_file.write_bytes(b"image")
    attachment = ProductAttachments(
        product_id=product.id,
        file_name="product.png",
        file_type="image/png",
        file_path=str(stored_file),
        created_by=1,
    )
    db_session.add(attachment)
    db_session.commit()
    db_session.refresh(attachment)

    response = client.delete(f"/products/attachments/{attachment.product_attachment_id}", headers=auth_headers)

    assert response.status_code == 403
    assert stored_file.exists()
    db_session.expire_all()
    assert db_session.get(ProductAttachments, attachment.product_attachment_id) is not None
