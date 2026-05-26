"""
CSV INGESTION PIPELINE
Handles structured CSV ingestion into SQLite
"""

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime


class CSVIngestion:

    def __init__(self, db_path="knowledge_base.db"):

        self.db_path = db_path

        self.engine = create_engine(
            f"sqlite:///{db_path}"
        )

        print("✓ CSV Ingestion Pipeline initialized")

    def ingest_csv(
        self,
        file_path,
        table_name,
        if_exists="replace"
    ):

        """
        Ingest CSV into SQLite database

        Args:
            file_path: Path to CSV file
            table_name: Database table name
            if_exists: replace / append / fail
        """

        try:

            print(f"\n📥 Ingesting CSV: {file_path}")

            df = pd.read_csv(file_path)

            # Clean column names
            df.columns = [
                col.strip().replace(" ", "_")
                for col in df.columns
            ]

            # Store in database
            df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=False
            )

            print("✓ CSV ingestion successful")

            return {

                "status": "success",

                "table_name": table_name,

                "rows_inserted": len(df),

                "columns": list(df.columns),

                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:

            print(f"❌ CSV ingestion failed: {e}")

            return {

                "status": "failed",

                "error": str(e),

                "timestamp": datetime.now().isoformat()
            }


# Example Usage
if __name__ == "__main__":

    ingestion = CSVIngestion()

    result = ingestion.ingest_csv(
        file_path="./data/csv_files/sample.csv",
        table_name="sales_data"
    )

    print(result)