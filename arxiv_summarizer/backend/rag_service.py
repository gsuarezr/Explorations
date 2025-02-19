import ollama
from typing import List, Dict
from .database import ArxivPaper
from .arxiv_service import PDFService

class RAGService:
    def __init__(self, topic: str, model_name: str = "llama2"):
        self.topic = topic
        self.model_name = model_name
        self.pdf_service = PDFService()
    
    def query_papers(self, papers: List[ArxivPaper], query: str) -> List[Dict]:
        results = []
        for paper in papers:
            content = self.pdf_service.extract_text(paper.pdf_path)
            
            prompt = f"""
            Based on this query: "{query}"
            
            How relevant is this paper?
            Title: {paper.title}
            Abstract: {paper.abstract}
            Content: {content[:3000]}
            
            Rate relevance (0-10) and explain why.
            """
            
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            results.append({
                'paper_id': paper.paper_id,
                'title': paper.title,
                'abstract': paper.abstract,
                'relevance_score': response['message']['content']
            })
        
        return sorted(results, 
                     key=lambda x: float(x['relevance_score'].split()[0]), 
                     reverse=True)

