import os
import requests
import time
from pathlib import Path
import logging
from dotenv import load_dotenv
import json
import mimetypes
import langdetect
import PyPDF2
from datetime import datetime

# Load environment variables
load_dotenv()

class CodeGPTDocumentManager:
    def __init__(self):
        # Get credentials from environment variables
        self.api_key = os.getenv('CODEGPT_API_KEY')
        self.organization_id = os.getenv('CODEGPT_ORG_ID')

        if not self.api_key or not self.organization_id:
            raise ValueError("API key or Organization ID not found in environment variables")

        self.base_url = "https://api-beta.codegpt.co/api/v1"

        # Headers setup
        self.headers = {
            "accept": "application/json",
            "CodeGPT-Org-Id": self.organization_id,
            "authorization": f"Bearer {self.api_key}"
        }

        # Define allowed file types and their size limits
        self.file_limits = {
            '.pdf': 20 * 1024 * 1024,  # 20MB
            '.doc': 20 * 1024 * 1024,  # 20MB
            '.docx': 20 * 1024 * 1024, # 20MB
            '.xls': 20 * 1024 * 1024,  # 20MB
            '.xlsx': 20 * 1024 * 1024, # 20MB
            '.pages': 20 * 1024 * 1024,# 20MB
            '.txt': 2 * 1024 * 1024,   # 2MB
            '.csv': 2 * 1024 * 1024    # 2MB
        }

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('document_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Add metadata templates
        self.metadata_template = {
            "title": "",
            "description": "",
            "summary": "",
            "keywords": "",
            "language": ""
        }

    def detect_language(self, text):
        """Detect the language of the text"""
        try:
            return langdetect.detect(text)
        except Exception as e:
            self.logger.warning(f"Language detection failed: {str(e)}")
            return "en"  # default to English if detection fails

    def extract_text_preview(self, file_path, max_chars=1000):
        """Extract text preview from file for metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(max_chars)
        except Exception as e:
            self.logger.warning(f"Text preview extraction failed: {str(e)}")
            return ""

    def generate_metadata(self, file_path):
        """Generate metadata for the document"""
        try:
            file_name = Path(file_path).stem
            extension = Path(file_path).suffix.lower()

            metadata = self.metadata_template.copy()

            # Set basic metadata
            metadata["title"] = file_name

            # Try to extract text preview for description and language detection
            if extension in ['.txt', '.csv']:
                preview_text = self.extract_text_preview(file_path)
                if preview_text:
                    # Detect language
                    metadata["language"] = self.detect_language(preview_text)

                    # Set description (first 200 characters)
                    metadata["description"] = preview_text[:200].strip()

                    # Set summary (next 500 characters)
                    metadata["summary"] = preview_text[200:700].strip()

                    # Generate keywords (simple implementation)
                    words = set(word.lower() for word in preview_text.split()[:50])
                    metadata["keywords"] = ", ".join(sorted(words)[:10])
            else:
                metadata["language"] = "en"  # default for non-text files
                metadata["description"] = f"Document uploaded from {file_path}"
                metadata["summary"] = f"Content of {file_name}"
                metadata["keywords"] = f"{extension[1:]}, document"

            return metadata
        except Exception as e:
            self.logger.error(f"Error generating metadata: {str(e)}")
            return self.metadata_template.copy()

    def get_file_type(self, file_path):
        """Get the file extension and mime type"""
        try:
            extension = Path(file_path).suffix.lower()
            mime_type = mimetypes.guess_type(file_path)[0]
            if mime_type is None:
                mime_type = 'application/octet-stream'
            return extension, mime_type
        except Exception as e:
            self.logger.error(f"Error getting file type: {str(e)}")
            return None, None

    def validate_file(self, file_path):
        """Validate file type and size"""
        try:
            extension = Path(file_path).suffix.lower()

            # Check if file type is supported
            if extension not in self.file_limits:
                self.logger.error(f"Unsupported file type: {extension}")
                return False

            # Check file size
            file_size = os.path.getsize(file_path)
            size_limit = self.file_limits[extension]

            self.logger.debug(f"File size: {file_size/1024/1024:.2f} MB")
            self.logger.debug(f"Size limit: {size_limit/1024/1024:.2f} MB")

            if file_size > size_limit:
                self.logger.error(f"File too large ({file_size/1024/1024:.2f}MB > {size_limit/1024/1024:.2f}MB): {file_path}")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating file: {str(e)}")
            return False
            def convert_pdf_to_text(self, pdf_path):
             """Convert PDF file to text"""
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        if not str(pdf_path).lower().endswith('.pdf'):
            self.logger.error(f"File is not a PDF: {pdf_path}")
            return None

        try:
            self.logger.info(f"Converting PDF to text: {pdf_path}")
            text_content = []

            with open(pdf_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                except Exception as e:
                    self.logger.error(f"Error reading PDF file: {str(e)}")
                    return None

                num_pages = len(pdf_reader.pages)
                self.logger.info(f"PDF has {num_pages} pages")

                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                        else:
                            self.logger.warning(f"No text extracted from page {page_num + 1}")
                    except Exception as e:
                        self.logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        continue

            if not text_content:
                self.logger.error("No text content extracted from PDF")
                return None

            full_text = "\n\n".join(text_content)
            text_filename = Path(pdf_path).stem + '.txt'
            text_filepath = Path(pdf_path).parent / text_filename

            try:
                with open(text_filepath, 'w', encoding='utf-8') as text_file:
                    text_file.write(full_text)
            except Exception as e:
                self.logger.error(f"Error saving text file: {str(e)}")
                return None

            self.logger.info(f"Successfully converted PDF to text: {text_filepath}")
            return text_filepath

        except Exception as e:
            self.logger.error(f"Error converting PDF to text: {str(e)}")
            return None

    def list_documents(self):
        """List all documents in the storage"""
        try:
            url = f"{self.base_url}/document"
            self.logger.info("Fetching document list...")

            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                documents = response.json()
                self.logger.info(f"Successfully retrieved {len(documents)} documents")

                print("\n=== Document Library ===")
                for doc in documents:
                    self.display_document_info(doc)

                return documents
            else:
                self.logger.error(f"Failed to fetch documents. Status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error listing documents: {str(e)}")
            return None

    def list_documents_with_ids(self):
        """List all documents with their IDs for deletion"""
        try:
            url = f"{self.base_url}/document"
            self.logger.info("Fetching document list...")

            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                documents = response.json()
                self.logger.info(f"Successfully retrieved {len(documents)} documents")

                print("\n=== Document Library ===")
                for doc in documents:
                    doc_id = doc.get('id', 'N/A')
                    doc_name = doc.get('name', 'N/A')
                    print(f"ID: {doc_id} - Name: {doc_name}")

                return documents
            else:
                self.logger.error(f"Failed to fetch documents. Status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error listing documents: {str(e)}")
            return None

    def delete_document(self, document_id):
        """Delete a document by its ID"""
        try:
            url = f"{self.base_url}/document/{document_id}"
            self.logger.info(f"Attempting to delete document with ID: {document_id}")

            response = requests.delete(url, headers=self.headers)

            if response.status_code in [200, 204]:
                self.logger.info(f"Successfully deleted document: {document_id}")
                print(f"Successfully deleted document: {document_id}")
                return True
            else:
                self.logger.error(f"Failed to delete document. Status code: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                print(f"Failed to delete document. Status code: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            print(f"Error deleting document: {str(e)}")
            return False

    def display_document_info(self, document):
        """Display formatted document information"""
        try:
            print("\nDocument Information:")
            print(f"ID: {document.get('id', 'N/A')}")
            print(f"Name: {document.get('name', 'N/A')}")
            print(f"Created: {document.get('created_at', 'N/A')}")
            print(f"File Type: {document.get('file_type', 'N/A')}")
            print("\nMetadata:")
            metadata = document.get('metadata', {})
            for key, value in metadata.items():
                print(f"  {key}: {value}")
            print(f"\nTokens: {document.get('tokens', 'N/A')}")
            print(f"Chunk Count: {document.get('chunk_count', 'N/A')}")
            print("-" * 50)
        except Exception as e:
            self.logger.error(f"Error displaying document info: {str(e)}")

    def upload_file(self, file_path):
        """Upload a single file with metadata to CodeGPT API"""
        try:
            upload_url = f"{self.base_url}/document"
            self.logger.debug(f"Attempting upload to: {upload_url}")

            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False

            extension, mime_type = self.get_file_type(file_path)
            if not extension or not mime_type:
                return False

            if not self.validate_file(file_path):
                return False

            metadata = self.generate_metadata(file_path)
            self.logger.debug(f"Generated metadata: {json.dumps(metadata, indent=2)}")

            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, mime_type)
                }
                data = {
                    'metadata': json.dumps(metadata)
                }

                try:
                    response = requests.post(
                        upload_url,
                        headers=self.headers,
                        files=files,
                        data=data,
                        timeout=30  # 30 seconds timeout
                    )

                    self.logger.debug(f"Response status code: {response.status_code}")
                    self.logger.debug(f"Response content: {response.text}")

                    if response.status_code in [200, 201]:
                        self.logger.info(f"Successfully uploaded: {file_path}")
                        return True
                    else:
                        self.logger.error(f"Failed to upload {file_path}. Status code: {response.status_code}")
                        self.logger.error(f"Response: {response.text}")
                        return False

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Network error during upload: {str(e)}")
                    return False

        except Exception as e:
            self.logger.error(f"Error uploading {file_path}: {str(e)}")
            return False

    def batch_process_files(self, directory_path):
        """Process and upload all supported files from a directory"""
        try:
            directory = Path(directory_path)
            self.logger.debug(f"Scanning directory: {directory.absolute()}")

            if not directory.exists():
                self.logger.error(f"Directory not found: {directory_path}")
                return

            supported_files = []
            for ext in self.file_limits.keys():
                supported_files.extend(directory.glob(f"**/*{ext}"))

            total_files = len(supported_files)
            if total_files == 0:
                self.logger.warning("No supported files found in the directory")
                print("No supported files found in the directory")
                return

            self.logger.info(f"Found {total_files} supported files to process")
            print(f"Found {total_files} supported files to process")

            successful_uploads = 0
            failed_uploads = []

            for index, file_path in enumerate(supported_files, 1):
                print(f"\nProcessing file {index}/{total_files}: {file_path}")
                self.logger.info(f"Processing file {index}/{total_files}: {file_path}")

                if file_path.suffix.lower() == '.pdf':
                    text_file = self.convert_pdf_to_text(str(file_path))
                    if text_file:
                        file_path = text_file
                    else:
                        failed_uploads.append(str(file_path))
                        continue

                if self.upload_file(str(file_path)):
                    successful_uploads += 1
                else:
                    failed_uploads.append(str(file_path))

                time.sleep(2)  # Rate limiting

            print("\nProcessing Summary:")
            print(f"Total files processed: {total_files}")
            print(f"Successfully uploaded: {successful_uploads}")
            print(f"Failed uploads: {len(failed_uploads)}")

            if failed_uploads:
                print("\nFailed uploads:")
                for file in failed_uploads:
                    print(file)

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            print(f"Error in batch processing: {str(e)}")

def main():
    """Main execution function"""
    try:
        print("Initializing CodeGPT Document Manager...")
        manager = CodeGPTDocumentManager()
        
        while True:
            try:
                print("\n=== CodeGPT Document Manager ===")
                print("1. Upload Documents")
                print("2. List Documents")
                print("3. Delete Document")
                print("4. Exit")
                
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == "1":
                    directory = input("\nEnter the path to your documents directory: ").strip()
                    if not directory:
                        print("Error: Directory path cannot be empty")
                        continue
                        
                    if os.path.exists(directory):
                        print(f"\nProcessing files from: {directory}")
                        manager.batch_process_files(directory)
                    else:
                        print(f"\nError: Directory not found: {directory}")
                
                elif choice == "2":
                    print("\nFetching document list...")
                    manager.list_documents()
                
                elif choice == "3":
                    print("\nFetching document list for deletion...")
                    documents = manager.list_documents_with_ids()
                    
                    if documents:
                        doc_id = input("\nEnter the ID of the document to delete (or 'cancel' to abort): ").strip()
                        
                        if doc_id.lower() == 'cancel':
                            print("Deletion cancelled")
                            continue
                            
                        confirm = input(f"\nAre you sure you want to delete document {doc_id}? (yes/no): ").strip().lower()
                        
                        if confirm == 'yes':
                            manager.delete_document(doc_id)
                        else:
                            print("Deletion cancelled")
                
                elif choice == "4":
                    print("\nExiting...")
                    break
                
                else:
                    print("\nInvalid choice. Please enter 1-4")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                continue
                
            except Exception as e:
                print(f"\nAn error occurred during operation: {str(e)}")
                logging.error(f"Operation error: {str(e)}")
                continue

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Critical error: {str(e)}")
        logging.error(f"Critical error in main execution: {str(e)}")
    finally:
        print("\nThank you for using CodeGPT Document Manager")

if __name__ == "__main__":
    main()
