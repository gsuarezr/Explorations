import arxiv
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from .database import Database,ArxivPaper
import PyPDF2

class PDFService:
    def extract_text(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

class ArxivService:
    def __init__(self, download_dir: str, db: Database):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.db = db
    
    def download_papers_for_topic(self, topic: str, keywords: List[str], days_back: int = 30):
        query = ' OR '.join(keywords)
        search = arxiv.Search(
            query=query,
            max_results=100,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        downloaded_papers = []
        for result in tqdm(search.results(), desc=f"Downloading {topic} papers"):
            pdf_path = self.download_dir / f"{result.get_short_id()}-v{result.version}.pdf"
            result.download_pdf(str(pdf_path))
            
            paper = ArxivPaper(
                paper_id=result.get_short_id(),
                title=result.title,
                abstract=result.summary,
                pdf_path=str(pdf_path),
                topics=[topic],
                downloaded_date=datetime.now().isoformat(),
                version=result.version
            )
            
            self.db.save_paper(paper)
            downloaded_papers.append(paper)
        
        return downloaded_papers