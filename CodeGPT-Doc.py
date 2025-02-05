import os
import requests
import time
import json
import mimetypes
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import langdetect
import PyPDF2

# Load environment variables
load_dotenv()

class CodeGPTDocumentManager:
    def __init__(self):
        # Get credentials from environment variables
        self.api_key = os.getenv('CODEGPT_API_KEY')
        self.organization_id = os.getenv('CODEGPT_ORG_ID')
        
        if not self.api_key or not self.organization_id:
            raise ValueError("API key or Organization ID not found in environment variables")

        self.base_url = "https://api.codegpt.co/api/v1"

        # Headers setup
        self.headers = {
            "accept": "application/json",
            "CodeGPT-Org-Id": self.organization_id,
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json"
        }

        # Setup logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def list_documents(self):
        """List all documents in the storage"""
        try:
            url = f"{self.base_url}/document"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Failed to fetch documents. Status: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error listing documents: {str(e)}")
            return None

    def delete_document(self, document_id):
        """Delete a document by its ID"""
        try:
            url = f"{self.base_url}/document/{document_id}"
            response = requests.delete(url, headers=self.headers)
            return response.status_code in [200, 204]
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            return False

    def delete_all_documents(self):
        """Delete all documents"""
        documents = self.list_documents()
        if documents:
            for doc in documents:
                doc_id = doc.get('id')
                if doc_id:
                    self.delete_document(doc_id)
                    print(f"Deleted document: {doc_id}")

    def upload_file(self, file_path):
        """Upload a document to CodeGPT API"""
        try:
            url = f"{self.base_url}/document"
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False

            extension = Path(file_path).suffix.lower()
            mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, mime_type)}
                response = requests.post(url, headers=self.headers, files=files)

            return response.status_code in [200, 201]
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            return False

    def update_metadata(self, document_id, metadata):
        """Update document metadata"""
        try:
            url = f"{self.base_url}/document/{document_id}/metadata"
            response = requests.patch(url, headers=self.headers, data=json.dumps(metadata))
            return response.status_code in [200, 204]
        except Exception as e:
            self.logger.error(f"Error updating metadata: {str(e)}")
            return False


def main():
    """Main execution function"""
    manager = CodeGPTDocumentManager()
    
    while True:
        print("\n=== CodeGPT Document Manager ===")
        print("1. Upload Document")
        print("2. List Documents")
        print("3. Delete Document")
        print("4. Delete All Documents")
        print("5. Update Metadata")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            file_path = input("Enter the path to the document: ").strip()
            if manager.upload_file(file_path):
                print("File uploaded successfully")
            else:
                print("Failed to upload file")
        
        elif choice == "2":
            documents = manager.list_documents()
            if documents:
                for doc in documents:
                    print(f"ID: {doc.get('id')} - Name: {doc.get('name')}")
            else:
                print("No documents found")
        
        elif choice == "3":
            doc_id = input("Enter document ID to delete: ").strip()
            if manager.delete_document(doc_id):
                print("Document deleted successfully")
            else:
                print("Failed to delete document")

        elif choice == "4":
            confirm = input("Are you sure you want to delete ALL documents? (yes/no): ").strip().lower()
            if confirm == "yes":
                manager.delete_all_documents()
                print("All documents deleted successfully")
            else:
                print("Deletion cancelled")

        elif choice == "5":
            doc_id = input("Enter document ID to update metadata: ").strip()
            title = input("Enter new title: ").strip()
            description = input("Enter description: ").strip()
            summary = input("Enter summary: ").strip()
            keywords = input("Enter keywords (comma separated): ").strip()
            language = input("Enter language code: ").strip()
            
            metadata = {
                "title": title,
                "description": description,
                "summary": summary,
                "keywords": keywords,
                "language": language
            }
            
            if manager.update_metadata(doc_id, metadata):
                print("Metadata updated successfully")
            else:
                print("Failed to update metadata")
        
        elif choice == "6":
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-6")

if __name__ == "__main__":
    main()
