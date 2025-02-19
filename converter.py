import sys
from pathlib import Path
import subprocess
import logging
from typing import List

class DocumentConverter:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the converter."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_dependencies(self) -> bool:
        """Check if required command-line tools are installed."""
        try:
            # Check for djvulibre-bin
            subprocess.run(['ddjvu', '--help'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            
            # Check for calibre
            subprocess.run(['ebook-convert', '--version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            self.logger.error("""
            Missing required dependencies. Please install:
            - djvulibre-bin (for djvu conversion)
            - calibre (for epub conversion)
            
            On Ubuntu/Debian:
            sudo apt-get install djvulibre-bin calibre
            
            On macOS:
            brew install djvulibre calibre
            """)
            return False

    def convert_djvu_to_pdf(self, file_path: Path) -> bool:
        """Convert a DjVu file to PDF."""
        try:
            output_path = file_path.with_suffix('.pdf')
            self.logger.info(f"Converting {file_path} to PDF...")
            
            process = subprocess.run(
                ['ddjvu', '-format=pdf', str(file_path), str(output_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.returncode == 0:
                self.logger.info(f"Successfully converted {file_path}")
                # Delete original file after successful conversion
                file_path.unlink()
                self.logger.info(f"Deleted original file: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to convert {file_path}: {process.stderr.decode()}")
                return False
        except Exception as e:
            self.logger.error(f"Error converting {file_path}: {str(e)}")
            return False

    def convert_epub_to_pdf(self, file_path: Path) -> bool:
        """Convert an EPUB file to PDF using Calibre's ebook-convert."""
        try:
            output_path = file_path.with_suffix('.pdf')
            self.logger.info(f"Converting {file_path} to PDF...")
            
            process = subprocess.run(
                ['ebook-convert', str(file_path), str(output_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.returncode == 0:
                self.logger.info(f"Successfully converted {file_path}")
                # Delete original file after successful conversion
                file_path.unlink()
                self.logger.info(f"Deleted original file: {file_path}")
                return True
            else:
                self.logger.error(f"Failed to convert {file_path}: {process.stderr.decode()}")
                return False
        except Exception as e:
            self.logger.error(f"Error converting {file_path}: {str(e)}")
            return False

    def cleanup_crdownload(self):
        """Remove all .crdownload files in the directory."""
        try:
            crdownload_files = list(self.directory.glob("*.crdownload"))
            for file in crdownload_files:
                file.unlink()
                self.logger.info(f"Deleted incomplete download: {file}")
        except Exception as e:
            self.logger.error(f"Error cleaning up .crdownload files: {str(e)}")

    def process_directory(self):
        """Process all files in the directory."""
        if not self.check_dependencies():
            return

        # Verify directory exists
        if not self.directory.exists():
            self.logger.error(f"Directory does not exist: {self.directory}")
            return
        
        if not self.directory.is_dir():
            self.logger.error(f"Path is not a directory: {self.directory}")
            return

        # Convert DjVu files
        for djvu_file in self.directory.glob("*.djvu"):
            self.convert_djvu_to_pdf(djvu_file)

        # Convert EPUB files
        for epub_file in self.directory.glob("*.epub"):
            self.convert_epub_to_pdf(epub_file)

        # Clean up .crdownload files
        self.cleanup_crdownload()

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        print("Example: python script.py /path/to/documents")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    converter = DocumentConverter(directory_path)
    converter.process_directory()

if __name__ == "__main__":
    main()