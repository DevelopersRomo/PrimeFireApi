import pytest
from PIL import Image

from services.expenses import dedupe
from services.expenses.ocr import engine, pdf, preprocess


def _letter_pdf(path):
    import pymupdf

    document = pymupdf.open()
    document.new_page(width=612, height=792)
    document.save(path)
    document.close()
    return path


def test_a_page_is_rendered_within_the_pixel_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf, "MAX_RENDER_PIXELS", 1_000_000)

    (image,) = pdf.render_pages(_letter_pdf(tmp_path / "letter.pdf"))

    height, width = image.shape[:2]
    assert height * width <= 1_000_000 * 1.01  # the pixmap rounds each side up


def test_a_page_inside_the_budget_keeps_its_full_resolution(tmp_path):
    (image,) = pdf.render_pages(_letter_pdf(tmp_path / "letter.pdf"))

    assert image.shape[:2] == (3300, 2550)  # 11 x 8.5 inches at 300 dpi


def test_tesseract_runs_with_a_deadline(monkeypatch):
    import numpy as np
    import pytesseract

    seen: dict = {}

    def fake_image_to_data(image, **kwargs):
        seen.update(kwargs)
        return {"text": []}

    monkeypatch.setattr(pytesseract, "image_to_data", fake_image_to_data)

    engine.recognise(np.zeros((10, 10, 3), dtype=np.uint8))

    assert 0 < seen["timeout"] <= 120


def test_an_image_beyond_the_pixel_budget_is_refused_before_decoding(tmp_path, monkeypatch):
    path = tmp_path / "huge.png"
    Image.new("RGB", (20, 20)).save(path)
    monkeypatch.setattr(preprocess, "MAX_IMAGE_PIXELS", 100)

    with pytest.raises(ValueError, match="pixels"):
        preprocess.load_image(path)
    assert dedupe.perceptual_hash(path) is None


def test_an_image_inside_the_budget_still_loads_and_hashes(tmp_path):
    path = tmp_path / "small.png"
    Image.new("RGB", (20, 20)).save(path)

    assert preprocess.load_image(path).shape == (20, 20, 3)
    assert dedupe.perceptual_hash(path) is not None
