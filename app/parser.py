import pandas as pd
from docx import Document
from pptx import Presentation
import json

# main function: parse 3 types of file

# converts tabular data into json or list of dictionary
def extract_from_excel(file_path):
    try:
        # asume the first row is the header
        df = pd.read_excel(file_path)
        # drop the rows that are completely empty 
        df = df.dropna(how='all')
        # Convert to a ist of dictionaries (each row beacomes one record)
        records = df.to_dict(orient="records")
        return json.dumps(records, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Excel parsing failed: {e}"

# extracts plain text paragrapg by paragraph
def extract_from_word(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())
        return "\n".join(full_text)
    except Exception as e:
        return f"Word parsing failed: {e}"
    
# iterates through every text box on every slide
def extract_from_ppt(file_path):
    try:
        prs = Presentation(file_path)
        text_runs = []

        for slide_num, slide in enumerate(prs.slides):
            slide_text = f"--- Slide {slide_num + 1} ---"
            text_runs.append(slide_text)
            
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_runs.append(shape.text.strip())
            
            return "\n".join(text_runs)
        
    except Exception as e:
        return f"PPT parsing failed: {e}"


# Testing
if __name__ == "__main__":
    print("--- Testing Excel Extraction ---")
    excel_data = extract_from_excel(r"C:\Users\YIXIN\Downloads\Lampiran A2 Senarai pelajar FAIX.xlsx")
    print(excel_data)

    print("--- Testing Word Extraction ---")
    word_text = extract_from_word(r"C:\Users\YIXIN\Downloads\EPI-script.docx")
    print(word_text)

    print("--- Testing PPT Extraction ---")
    ppt_text = extract_from_ppt(r"C:\Users\YIXIN\Downloads\Chapter 6_Estimation_v4_sakinah.pptx")
    print(ppt_text)