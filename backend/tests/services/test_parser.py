import pytest
import json
import os
from app.services.parser import extract_from_excel, extract_from_word, extract_from_ppt, extract_from_pdf


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")

def test_extract_from_excel_success():
    file_path = os.path.join(TEST_DATA_DIR, "simple.xlsx")
    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")

    result = extract_from_excel(file_path)
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]

def test_extract_from_excel_failure():
    result = extract_from_excel("fake_path.xlsx")
    assert isinstance(result, str)
    assert "Excel parsing failed" in result

def test_extract_from_word_success():
    file_path = os.path.join(TEST_DATA_DIR, "simple.docx")
    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")

    result = extract_from_word(file_path)
    assert isinstance(result, str)
    assert len(result) > 0

def test_extract_from_word_failure():
    result = extract_from_word("fake_path.docx")
    assert "Word parsing failed" in result

def test_extract_from_ppt_success():
    file_path = os.path.join(TEST_DATA_DIR, "simple.pptx")

    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")
                    
    result = extract_from_ppt(str(file_path))
       
    assert isinstance(result, str)
    assert "--- Slide 1 ---" in result

def test_extract_from_ppt_failure():
    result = extract_from_ppt("non_existent_file.pptx")

    assert isinstance(result, str)
    assert result.startswith("PPT parsing failed:")


def test_extract_from_pdf_text_only():
    file_path = os.path.join(TEST_DATA_DIR, "text_only.pdf")
    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")
    
    result = extract_from_pdf(file_path)
    assert "--- Page 1 ---" in result
    assert "[OCR]" not in result

def test_extract_from_pdf_requires_ocr():
    file_path = os.path.join(TEST_DATA_DIR, "image.pdf")
    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")

    result = extract_from_pdf(str(file_path))
    assert isinstance(result, str)

def test_extract_from_pdf_empty():
    file_path = os.path.join(TEST_DATA_DIR, "empty.pdf")
    if not os.path.exists(file_path):
        pytest.skip(f"skip: file not found {file_path}")

    result = extract_from_pdf(str(file_path))
    assert result == "\n --- Page 1 ---"

def test_extract_from_pdf_failure():
    result = extract_from_pdf("fake.pdf")
    assert isinstance(result, str)
    assert result.startswith("PDF parsing failed:")
