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
        except:
            return "en"  # default to English if detection fails

    def extract_text_preview(self, file_path, max_chars=1000):
        """Extract text preview from file for metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(max_chars)
        except:
            return ""

    def generate_metadata(self, file_path):
        """Generate metadata for the document"""
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

    def get_file_type(self, file_path):
        """Get the file extension and mime type"""
        extension = Path(file_path).suffix.lower()
        mime_type = mimetypes.guess_type(file_path)[0]
        return extension, mime_type

    def validate_file(self, file_path):
        """Validate file type and size"""
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

    def convert_pdf_to_text(self, pdf_path):
        """Convert PDF file to text"""
        try:
            self.logger.info(f"Converting PDF to text: {pdf_path}")
            text_content = []

            with open(pdf_path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)

                # Get number of pages
                num_pages = len(pdf_reader.pages)
                self.logger.info(f"PDF has {num_pages} pages")

                # Extract text from each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text_content.append(page.extract_text())

            # Join all pages with double newlines
            full_text = "\n\n".join(text_content)

            # Create text filename
            text_filename = Path(pdf_path).stem + '.txt'
            text_filepath = Path(pdf_path).parent / text_filename

            # Save text content
            with open(text_filepath, 'w', encoding='utf-8') as text_file:
                text_file.write(full_text)

            self.logger.info(f"Successfully converted PDF to text: {text_filepath}")
            return text_filepath

        except Exception as e:
            self.logger.error(f"Error converting PDF to text: {str(e)}")
            return None

    def upload_file(self, file_path):
        """Upload a single file with metadata to CodeGPT API"""
        try:
            upload_url = f"{self.base_url}/document"
            self.logger.debug(f"Attempting upload to: {upload_url}")

            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False

            # Get file extension and mime type
            extension, mime_type = self.get_file_type(file_path)

            # Validate file type and size
            if not self.validate_file(file_path):
                return False

            # Generate metadata
            metadata = self.generate_metadata(file_path)
            self.logger.debug(f"Generated metadata: {json.dumps(metadata, indent=2)}")

            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, mime_type)
                }

                # Add metadata to the request
                data = {
                    'metadata': json.dumps(metadata)
                }

                response = requests.post(
                    upload_url,
                    headers=self.headers,
                    files=files,
                    data=data
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

            # Get all files with supported extensions
            supported_files = []
            for ext in self.file_limits.keys():
                supported_files.extend(directory.glob(f"**/*{ext}"))

            total_files = len(supported_files)

            if total_files == 0:
                self.logger.warning("No supported files found in the directory")
                return

            self.logger.info(f"Found {total_files} supported files to process")

            successful_uploads = 0
            failed_uploads = []

            for index, file_path in enumerate(supported_files, 1):
                self.logger.info(f"Processing file {index}/{total_files}: {file_path}")

                # Convert PDF to text if necessary
                if file_path.suffix.lower() == '.pdf':
                    text_file = self.convert_pdf_to_text(str(file_path))
                    if text_file:
                        file_path = text_file
                    else:
                        failed_uploads.append(str(file_path))
                        continue

                # Upload file
                if self.upload_file(str(file_path)):
                    successful_uploads += 1
                else:
                    failed_uploads.append(str(file_path))

                # Add delay between uploads
                time.sleep(2)

            # Log summary
            self.logger.info(f"\nProcessing Summary:")
            self.logger.info(f"Total files processed: {total_files}")
            self.logger.info(f"Successfully uploaded: {successful_uploads}")
            self.logger.info(f"Failed uploads: {len(failed_uploads)}")

            if failed_uploads:
                self.logger.info("\nFailed uploads:")
                for file in failed_uploads:
                    self.logger.info(file)

        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")

    def display_document_info(self, document):
        """Display formatted document information"""
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

    def list_documents(self):
        """List all documents in the storage with formatted output"""
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

def main():
    try:
        # Install required packages
        os.system('pip install python-dotenv requests langdetect PyPDF2')

        manager = CodeGPTDocumentManager()

        while True:
            print("\n=== CodeGPT Document Manager ===")
            print("1. List Documents")
            print("2. Upload New Documents")
            print("3. Exit")

            choice = input("\nEnter your choice (1-3): ")

            if choice == "1":
                manager.list_documents()

            elif choice == "2":
                directory = os.getenv('DOCUMENT_DIRECTORY')
                if not directory:
                    directory = input("\nEnter the path to your documents directory: ")

                proceed = input(f"\nProceed with processing files from {directory}? (y/n): ")

                if proceed.lower() == 'y':
                    manager.batch_process_files(directory)

            elif choice == "3":
                print("\nExiting...")
                break

            else:
                print("\nInvalid choice. Please try again.")

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
