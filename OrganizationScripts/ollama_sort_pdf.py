# import os
# import json
# import shutil
# from pathlib import Path
# import PyPDF2
# import ollama
# import sys
# from tqdm import tqdm  # Add tqdm for progress bar
# from typing import Dict, List

# class PDFOrganizer:
#     def __init__(self, source_dir: str, config_file: str = "folder_categories.json"):
#         self.source_dir = Path(source_dir)
#         self.config_file = config_file
#         self.categories = self._load_categories()
        
#     def _load_categories(self) -> Dict[str, List[str]]:
#         """Load existing categories from config file if it exists."""
#         if os.path.exists(self.config_file):
#             with open(self.config_file, 'r') as f:
#                 return json.load(f)
#         return {}

#     def _save_categories(self):
#         """Save categories to config file."""
#         with open(self.config_file, 'w') as f:
#             json.dump(self.categories, f, indent=4)

#     def extract_text_from_pdf(self, pdf_path: Path) -> str:
#         """Extract text content from a PDF file."""
#         try:
#             text = ""
#             with open(pdf_path, 'rb') as file:
#                 reader = PyPDF2.PdfReader(file)
#                 for page in reader.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#             if not text:
#                 print(f"⚠️ No text extracted from {pdf_path}")
#             return text[:1_000]  # Limit to first 1,000 characters
#         except Exception as e:
#             print(f"⚠️ Error reading PDF {pdf_path}: {e}")
#             return ""

#     def get_category(self, text: str) -> str:
#         """Use Ollama to determine the category for the text."""
#         prompt = f"""
#         Based on the following text from a PDF, suggest a single category name that best describes its content.
#         The category name should be simple and generic enough to group similar documents.
#         Only respond with the category name in lowercase, no other text.

#         Text:
#         {text}
#         """

#         try:
#             response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
#             category = response.get('message', {}).get('content', "").strip().lower()
#             print(response)
#             if not category:
#                 print("⚠️ Ollama returned an empty category. Check model response.")
#                 return "uncategorized"
#             return category
#         except Exception as e:
#             print(f"⚠️ Error querying Ollama: {e}")
#             return "uncategorized"  # Default folder if Ollama fails

#     def organize_pdfs(self):
#         """Organize PDFs into folders based on their categorized content."""
#         pdf_files = list(self.source_dir.glob("*.pdf"))
#         processed_files = set()

#         if not pdf_files:
#             print("No PDFs found in the source directory.")
#             return

#         print(f"Processing {len(pdf_files)} PDFs...")

#         # Use tqdm for a progress bar
#         with tqdm(total=len(pdf_files), desc="Processing PDFs", unit="file") as progress_bar:
#             for pdf_path in pdf_files:
#                 if pdf_path.name in processed_files:
#                     progress_bar.update(1)
#                     continue

#                 # Extract text from PDF
#                 text = self.extract_text_from_pdf(pdf_path)
#                 if not text:
#                     print(f"⚠️ Skipping {pdf_path.name} due to extraction failure.")
#                     progress_bar.update(1)
#                     continue

#                 # Get category for the PDF
#                 category = self.get_category(text)
#                 print(f"📂 Categorizing {pdf_path.name} as '{category}'")
                
#                 # Ensure category is valid before moving
#                 if not category:
#                     print(f"⚠️ No category assigned for {pdf_path.name}, skipping.")
#                     progress_bar.update(1)
#                     continue

#                 category_dir = self.source_dir / category
#                 category_dir.mkdir(exist_ok=True)

#                 try:
#                     shutil.move(str(pdf_path), str(category_dir / pdf_path.name))
#                     processed_files.add(pdf_path.name)
#                     print(f"✅ Moved {pdf_path.name} to {category}/")

#                     # Update categories dictionary
#                     if category not in self.categories:
#                         self.categories[category] = []
#                     self.categories[category].append(pdf_path.name)
#                 except Exception as e:
#                     print(f"⚠️ Error moving {pdf_path}: {e}")

#                 progress_bar.update(1)

#         # Save updated categories
#         self._save_categories()
#         print("📂 PDF organization completed.")

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: python script.py <source_directory>")
#         sys.exit(1)
    
#     path = sys.argv[1]
#     print(f"📂 Source directory: {path}")
#     organizer = PDFOrganizer(path)
#     organizer.organize_pdfs()



# import os
# import json
# import shutil
# from pathlib import Path
# import PyPDF2
# import ollama
# import sys
# import asyncio
# from tqdm import tqdm  # Add tqdm for progress bar
# from typing import Dict, List

# class PDFOrganizer:
#     def __init__(self, source_dir: str, config_file: str = "folder_categories.json"):
#         self.source_dir = Path(source_dir)
#         self.config_file = config_file
#         self.categories = self._load_categories()
        
#     def _load_categories(self) -> Dict[str, List[str]]:
#         """Load existing categories from config file if it exists."""
#         if os.path.exists(self.config_file):
#             with open(self.config_file, 'r') as f:
#                 return json.load(f)
#         return {}
    
#     def _save_categories(self):
#         """Save categories to config file."""
#         with open(self.config_file, 'w') as f:
#             json.dump(self.categories, f, indent=4)

#     async def extract_text_from_pdf(self, pdf_path: Path) -> str:
#         """Extract text content from a PDF file asynchronously."""
#         return await asyncio.to_thread(self._extract_text_sync, pdf_path)

#     def _extract_text_sync(self, pdf_path: Path) -> str:
#         """Extract text synchronously, for use with asyncio.to_thread."""
#         try:
#             text = ""
#             with open(pdf_path, 'rb') as file:
#                 reader = PyPDF2.PdfReader(file)
#                 for page in reader.pages:
#                     text += page.extract_text() + "\n"
#             return text[:24_000]  # Limit to first 24,000 characters
#         except Exception as e:
#             print(f"Error reading PDF {pdf_path}: {e}")
#             return ""

#     async def get_category(self, text: str) -> str:
#         """Use Ollama to determine the category for the text."""
#         prompt = f"""
#         Based on the following text from a PDF, suggest a single category name that best describes its content.
#         The category name should be simple and generic enough to group similar documents. But also specific enough
#         so that a document about quantum field theory in cosmology and a text in quantum mechanics end up in different
#         groups.
#         Only respond with the category name in lowercase, no other text.

#         Text:
#         {text}
#         """
        
#         response = await asyncio.to_thread(
#             ollama.chat, model='deepseek-r1:7b', messages=[{'role': 'user', 'content': prompt}]
#         )
        
#         return response['message']['content'].strip().lower()

#     async def organize_pdfs(self):
#         """Main function to organize PDFs into categories using async for performance."""
#         pdf_files = list(self.source_dir.glob("*.pdf"))
#         processed_files = set()
        
#         if not pdf_files:
#             print("No PDFs found in the source directory.")
#             return

#         print(f"Processing {len(pdf_files)} PDFs...")

#         # Use tqdm for a progress bar
#         progress_bar = tqdm(total=len(pdf_files), desc="Processing PDFs", unit="file")

#         async def process_pdf(pdf_path: Path):
#             """Process a single PDF asynchronously."""
#             if pdf_path.name in processed_files:
#                 progress_bar.update(1)
#                 return

#             text = await self.extract_text_from_pdf(pdf_path)
#             if not text:
#                 progress_bar.update(1)
#                 return

#             category = await self.get_category(text)

#             # Create category folder if it doesn't exist
#             category_dir = self.source_dir / category
#             category_dir.mkdir(exist_ok=True)

#             # Move PDF to category folder
#             try:
#                 shutil.move(str(pdf_path), str(category_dir / pdf_path.name))
#                 processed_files.add(pdf_path.name)

#                 # Update categories dictionary
#                 if category not in self.categories:
#                     self.categories[category] = []
#                 self.categories[category].append(pdf_path.name)

#             except Exception as e:
#                 print(f"Error moving {pdf_path}: {e}")

#             progress_bar.update(1)

#         # Run processing concurrently
#         await asyncio.gather(*[process_pdf(pdf) for pdf in pdf_files])

#         # Save updated categories
#         self._save_categories()
#         progress_bar.close()
#         print("PDF organization completed.")

# async def main():
#     path = sys.argv[1]
#     print(f"Source directory: {path}")
#     organizer = PDFOrganizer(path)
#     await organizer.organize_pdfs()

# if __name__ == "__main__":
#     asyncio.run(main())  # Run async main function



# import os
# import json
# import shutil
# from pathlib import Path
# import PyPDF2
# from typing import Dict, List
# import ollama
# import sys
# import asyncio  

# class PDFOrganizer:
#     def __init__(self, source_dir: str, config_file: str = "folder_categories.json"):
#         self.source_dir = Path(source_dir)
#         self.config_file = config_file
#         self.categories = self._load_categories()
        
#     def _load_categories(self) -> Dict[str, List[str]]:
#         """Load existing categories from config file if it exists."""
#         if os.path.exists(self.config_file):
#             with open(self.config_file, 'r') as f:
#                 return json.load(f)
#         return {}
    
#     def _save_categories(self):
#         """Save categories to config file."""
#         with open(self.config_file, 'w') as f:
#             json.dump(self.categories, f, indent=4)
    
#     def extract_text_from_pdf(self, pdf_path: Path) -> str:
#         """Extract text content from a PDF file."""
#         try:
#             text = ""
#             with open(pdf_path, 'rb') as file:
#                 reader = PyPDF2.PdfReader(file)
#                 for page in reader.pages:
#                     text += page.extract_text() + "\n"
#             return text[:24_000]  # Limit text to first 24_000 characters for analysis around 10 pages
#         except Exception as e:
#             print(f"Error reading PDF {pdf_path}: {e}")
#             return ""

#     async def get_category(self, text: str) -> str:
#         """Use Ollama to determine the category for the text."""
#         prompt = f"""
#         Based on the following text from a PDF, suggest a single category name that best describes its content.
#         The category name should be simple and generic enough to group similar documents. But also specific enough
#         so that a document about quantum field theory in cosmology and a text in quantum mechanics end up in different
#         groups.
#         Only respond with the category name in lowercase, no other text.
        
#         Text:
#         {text}
#         """
        
#         response = ollama.chat(model='deepseek-r1:7b', messages=[
#             {
#                 'role': 'user',
#                 'content': prompt
#             }
#         ])
        
#         category = response['message']['content'].strip().lower()
#         return category

#     async def organize_pdfs(self):
#         """Main function to organize PDFs into categories."""
#         processed_files = set()
        
#         for pdf_path in self.source_dir.glob("*.pdf"):
#             if pdf_path.name in processed_files:
#                 continue
                
#             text = self.extract_text_from_pdf(pdf_path)
#             if not text:
#                 continue
            
#             category = await self.get_category(text)  # <-- Add await here
            
#             category_dir = self.source_dir / category
#             category_dir.mkdir(exist_ok=True)
            
#             try:
#                 shutil.move(str(pdf_path), str(category_dir / pdf_path.name))
#                 processed_files.add(pdf_path.name)
                
#                 if category not in self.categories:
#                     self.categories[category] = []
#                 self.categories[category].append(pdf_path.name)
            
#             except Exception as e:
#                 print(f"Error moving {pdf_path}: {e}")
        
#         self._save_categories()

        
# async def main():
#     path = sys.argv[1]
#     print(path)
#     organizer = PDFOrganizer(path)
#     await organizer.organize_pdfs()  # Use await here
    
# if __name__ == "__main__":
#     # Initialize and run the organizer
#     asyncio.run(main())  # Use asyncio.run()


import os
import json
import shutil
import sys
from pathlib import Path
import PyPDF2
import ollama
from tqdm import tqdm  # Progress bar
from typing import Dict, List, Optional

class PDFOrganizer:
    def __init__(self, source_dir: str, config_file: str = "folder_categories.json"):
        self.source_dir = Path(source_dir)
        self.config_file = config_file
        self.categories = self._load_categories()
        
    def _load_categories(self) -> Dict[str, List[str]]:
        """Load existing categories from the config file if it exists."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_categories(self):
        """Save categories to the config file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.categories, f, indent=4)

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file, handling errors properly."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text + "\n"
            return text[:1_00]  # Limit extracted text for processing
        except Exception as e:
            print(f"⚠️ Error reading PDF {pdf_path}: {e}")
            return ""

    def get_category(self, text: str) -> str:
        """Use Ollama to determine the category, with error handling."""
        if not text:
            return "uncategorized"

        prompt = f"""
        Based on the following text from a PDF, suggest a single category name that best describes its content.
        The category name should be simple and generic enough to group similar documents. But also specific enough
        so that a document about quantum field theory in cosmology and a text in quantum mechanics end up in different
        groups.
        
        Important:Only respond with the category name in lowercase, no other text.

        Text:
        {text}
        """

        try:
            response = ollama.chat(model='deepseek-r1:1.5b', messages=[{'role': 'user', 'content': prompt}])
            
            category = response.message.content.strip().lower()    
            category = category.split("\n")[-1].strip()
            
        # Ensure the category name is filesystem-safe
            category = category.replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-")\
                            .replace("?", "-").replace("\"", "-").replace("<", "-").replace(">", "-")\
                            .replace("|", "-")

            if not category:  # Handle empty responses
                print("⚠️ Ollama returned an empty response. Assigning 'uncategorized'.")
                return "uncategorized"
            
            return category
        
        except Exception as e:
            print(f"⚠️ Ollama API error: {e}. Assigning 'uncategorized'.")
            return "uncategorized"

    def organize_pdfs(self):
        """Organize PDFs into folders based on their categorized content."""
        pdf_files = list(self.source_dir.glob("*.pdf"))
        processed_files = set()

        if not pdf_files:
            print("No PDFs found in the source directory.")
            return

        print(f"📂 Processing {len(pdf_files)} PDFs...")

        # Use tqdm for a progress bar
        with tqdm(total=len(pdf_files), desc="Processing PDFs", unit="file") as progress_bar:
            for pdf_path in pdf_files:
                if pdf_path.name in processed_files:
                    progress_bar.update(1)
                    continue

                # Extract text from PDF
                text = self.extract_text_from_pdf(pdf_path)
                if not text:
                    print(f"⚠️ No text extracted from {pdf_path}, skipping.")
                    progress_bar.update(1)
                    continue

                # Get category for the PDF
                category = self.get_category(text)
                print(f"📄 {pdf_path.name} → 🏷️ Category: {category}")

                # Create category folder if it doesn't exist
                category_dir = self.source_dir / category
                category_dir.mkdir(exist_ok=True)

                # Move PDF to category folder
                try:
                    shutil.move(str(pdf_path), str(category_dir / pdf_path.name))
                    processed_files.add(pdf_path.name)

                    # Update categories dictionary
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(pdf_path.name)

                except Exception as e:
                    print(f"⚠️ Error moving {pdf_path}: {e}")

                progress_bar.update(1)

        # Save updated categories
        self._save_categories()
        print("✅ PDF organization completed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python organize_pdfs.py <source_directory>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"📂 Source directory: {path}")
    organizer = PDFOrganizer(path)
    organizer.organize_pdfs()
