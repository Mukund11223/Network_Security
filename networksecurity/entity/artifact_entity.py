from dataclasses import dataclass

@dataclass ## acts like a decorator which creates variables for the empty class (we need to define variables without any functions )
class DataIngestionArtifact: ## this defines the final output of the data ingestion from the data ingestion component
    trained_file_path:str
    test_file_path:str


