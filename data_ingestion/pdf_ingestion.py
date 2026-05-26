"""
PDF INGESTION PIPELINE
Extracts text from PDFs and stores documents
for retrieval and RAG indexing
"""

from pypdf import PdfReader
from pathlib import Path
from datetime import datetime


class PDFIngestion:

    def __init__(
        self,
        documents_path="./data/documents"
    ):

        self.documents_path = Path(documents_path)

        self.documents_path.mkdir(
            parents=True,
            exist_ok=True
        )

        print("✓ PDF Ingestion Pipeline initialized")

    def extract_text(self, pdf_path):

        """
        Extract text from PDF
        """

        try:

            print(f"\n📄 Processing PDF: {pdf_path}")

            reader = PdfReader(pdf_path)

            text = ""

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:

                    text += extracted + "\n"

            return text

        except Exception as e:

            print(f"❌ PDF extraction failed: {e}")

            return None

    def ingest_pdf(self, pdf_path):

        """
        Extract and store PDF text
        """

        text = self.extract_text(pdf_path)

        if not text:

            return {

                "status": "failed",

                "error": "No text extracted"
            }

        output_file = (
            self.documents_path /
            f"{Path(pdf_path).stem}.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:

            f.write(text)

        print("✓ PDF ingestion successful")

        return {

            "status": "success",

            "document": str(output_file),

            "characters_extracted": len(text),

            "timestamp": datetime.now().isoformat()
        }


# Example Usage
if __name__ == "__main__":

    ingestion = PDFIngestion()

    result = ingestion.ingest_pdf(
        "./data/documents/sample.pdf"
    )

    print(result)