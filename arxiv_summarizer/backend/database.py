import sqlite3
import json
from contextlib import contextmanager
from typing import List
from dataclasses import dataclass
from typing import List

@dataclass
class ArxivPaper:
    paper_id: str
    title: str
    abstract: str
    pdf_path: str
    topics: List[str]
    downloaded_date: str
    version: int
    
class Database:
    def __init__(self, db_path: str = "arxiv_papers.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT,
                    abstract TEXT,
                    pdf_path TEXT,
                    topics TEXT,
                    downloaded_date TEXT,
                    version INTEGER
                )
            """)
    
    def save_paper(self, paper: ArxivPaper):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO papers
                (paper_id, title, abstract, pdf_path, topics, downloaded_date, version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.paper_id,
                paper.title,
                paper.abstract,
                paper.pdf_path,
                json.dumps(paper.topics),
                paper.downloaded_date,
                paper.version
            ))

    def get_papers_by_topic(self, topic: str) -> List[ArxivPaper]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM papers WHERE topics LIKE ?",
                (f'%{topic}%',)
            )
            return [
                ArxivPaper(
                    paper_id=row[0],
                    title=row[1],
                    abstract=row[2],
                    pdf_path=row[3],
                    topics=json.loads(row[4]),
                    downloaded_date=row[5],
                    version=row[6]
                )
                for row in cursor.fetchall()
            ]