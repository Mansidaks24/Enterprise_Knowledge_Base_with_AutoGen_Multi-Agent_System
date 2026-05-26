from data_ingestion.csv_ingestion import CSVIngestion

ingestion = CSVIngestion()

result = ingestion.ingest_csv(
    file_path="./data/csv_files/employees.csv",
    table_name="employees"
)

print(result)