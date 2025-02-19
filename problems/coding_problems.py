import requests
from bs4 import BeautifulSoup
import random
import os
from pathlib import Path
import json
import re
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import time

class ProblemSource(Enum):
    PROJECT_EULER = "project_euler"
    LEETCODE = "leetcode"
    HACKERRANK = "hackerrank"

@dataclass
class Problem:
    id: str
    title: str
    content: str
    source: ProblemSource
    url: str
    difficulty: str
    topics: List[str]

class ProblemFetcher:
    def __init__(self, cache_file="problem_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.session = requests.Session()
        
        # Headers to mimic browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_cache(self) -> dict:
        """Load previously fetched problems from cache."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {
            "solved": [],
            "fetched": {
                "project_euler": [],
                "leetcode": [],
                "hackerrank": []
            }
        }

    def _save_cache(self):
        """Save fetched problems to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def fetch_project_euler(self) -> Optional[Problem]:
        """Fetch a random Project Euler problem."""
        problem_id = random.randint(1, 800)
        while problem_id in self.cache["fetched"]["project_euler"]:
            problem_id = random.randint(1, 800)

        url = f"https://projecteuler.net/problem={problem_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            problem_content = soup.find('div', class_='problem_content')
            if not problem_content:
                return None
            
            problem = Problem(
                id=str(problem_id),
                title=soup.find('h2').text.strip(),
                content=problem_content.text.strip(),
                source=ProblemSource.PROJECT_EULER,
                url=url,
                difficulty="N/A",
                topics=["mathematics", "programming"]
            )
            
            self.cache["fetched"]["project_euler"].append(problem_id)
            self._save_cache()
            return problem
        except Exception as e:
            print(f"Error fetching Project Euler problem: {e}")
            return None

    def fetch_leetcode(self) -> Optional[Problem]:
        """Fetch a random LeetCode problem using their API."""
        api_url = "https://leetcode.com/api/problems/all/"
        graphql_url = "https://leetcode.com/graphql"
        
        try:
            # Get list of all problems
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            problems_list = response.json()['stat_status_pairs']
            
            # Filter out premium problems and already fetched ones
            available_problems = [
                p for p in problems_list 
                if not p['paid_only'] and 
                str(p['stat']['frontend_question_id']) not in self.cache["fetched"]["leetcode"]
            ]
            
            if not available_problems:
                return None
                
            # Select random problem
            problem_data = random.choice(available_problems)
            problem_title_slug = problem_data['stat']['question__title_slug']
            
            # Fetch detailed problem data
            query = """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                questionId
                title
                content
                difficulty
                topicTags {
                    name
                }
              }
            }
            """
            
            response = requests.post(
                graphql_url,
                headers=self.headers,
                json={
                    'query': query,
                    'variables': {'titleSlug': problem_title_slug}
                }
            )
            response.raise_for_status()
            
            question_data = response.json()['data']['question']
            
            problem = Problem(
                id=question_data['questionId'],
                title=question_data['title'],
                content=BeautifulSoup(question_data['content'], 'html.parser').get_text(),
                source=ProblemSource.LEETCODE,
                url=f"https://leetcode.com/problems/{problem_title_slug}",
                difficulty=question_data['difficulty'],
                topics=[tag['name'] for tag in question_data['topicTags']]
            )
            
            self.cache["fetched"]["leetcode"].append(problem.id)
            self._save_cache()
            return problem
            
        except Exception as e:
            print(f"Error fetching LeetCode problem: {e}")
            return None

    def fetch_hackerrank(self) -> Optional[Problem]:
        """Fetch a random HackerRank problem."""
        # HackerRank tracks API usage more strictly, so we'll use their public problem list
        base_url = "https://www.hackerrank.com/domains/algorithms"
        
        try:
            response = requests.get(base_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract problem links
            problem_links = soup.find_all('a', href=re.compile(r'/challenges/[^/]+/problem'))
            
            # Filter out already fetched problems
            available_problems = [
                link for link in problem_links 
                if link['href'].split('/')[-2] not in self.cache["fetched"]["hackerrank"]
            ]
            
            if not available_problems:
                return None
                
            # Select random problem
            problem_link = random.choice(available_problems)
            problem_url = f"https://www.hackerrank.com{problem_link['href']}"
            
            response = requests.get(problem_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            problem_id = problem_link['href'].split('/')[-2]
            problem = Problem(
                id=problem_id,
                title=soup.find('h1', class_='challenge-title').text.strip(),
                content=soup.find('div', class_='challenge-body-html').text.strip(),
                source=ProblemSource.HACKERRANK,
                url=problem_url,
                difficulty=soup.find('span', class_='difficulty').text.strip(),
                topics=["algorithms"]  # HackerRank organizes by domains
            )
            
            self.cache["fetched"]["hackerrank"].append(problem_id)
            self._save_cache()
            return problem
            
        except Exception as e:
            print(f"Error fetching HackerRank problem: {e}")
            return None

    def setup_local_environment(self, problem: Problem) -> str:
        """Create a local development environment for the problem."""
        base_dir = Path(f"problems/{problem.source.value}/problem_{problem.id}")
        base_dir.mkdir(parents=True, exist_ok=True)

        # Create README with problem description
        readme_content = f"""# {problem.title}
Problem ID: {problem.id}
Source: {problem.source.value.title()}
URL: {problem.url}
Difficulty: {problem.difficulty}
Topics: {', '.join(problem.topics)}

## Description
{problem.content}

## Notes
- Add your notes here
- Break down the problem
- Plan your approach

## Test Cases
- Add test cases here
"""
        readme_path = base_dir / "README.md"
        readme_path.write_text(readme_content)

        # Create solution templates for different languages
        templates = {
            "python": """def solve():
    # Your solution here
    pass

def test_solution():
    # Add your test cases here
    assert solve() == None  # Replace None with expected answer

if __name__ == "__main__":
    test_solution()
    result = solve()
    print(f"Solution: {result}")
""",
            "java": """public class Solution {
    public static void solve() {
        // Your solution here
    }
    
    public static void main(String[] args) {
        solve();
    }
}
""",
            "javascript": """function solve() {
    // Your solution here
}

function testSolution() {
    // Add your test cases here
    console.assert(solve() === null, "Replace null with expected answer");
}

if (require.main === module) {
    testSolution();
    console.log(`Solution: ${solve()}`);
}
"""
        }

        # Create solution files for each language
        for lang, template in templates.items():
            ext = ".py" if lang == "python" else ".java" if lang == "java" else ".js"
            solution_path = base_dir / f"solution{ext}"
            if not solution_path.exists():
                solution_path.write_text(template)

        return str(base_dir)

    def get_random_problem(self, source: Optional[ProblemSource] = None) -> Optional[Problem]:
        """Fetch a random problem from specified source or any source."""
        if source:
            fetch_methods = {
                ProblemSource.PROJECT_EULER: self.fetch_project_euler,
                ProblemSource.LEETCODE: self.fetch_leetcode,
                ProblemSource.HACKERRANK: self.fetch_hackerrank
            }
            return fetch_methods[source]()
        
        # Try all sources in random order
        sources = list(ProblemSource)
        random.shuffle(sources)
        
        for source in sources:
            problem = self.get_random_problem(source)
            if problem:
                return problem
        
        return None

def main():
    fetcher = ProblemFetcher()
    
    print("Choose problem source:")
    print("1. Project Euler")
    print("2. LeetCode")
    print("3. HackerRank")
    print("4. Random (any source)")
    
    choice = input("\nEnter your choice (1-4): ")
    source_map = {
        "1": ProblemSource.PROJECT_EULER,
        "2": ProblemSource.LEETCODE,
        "3": ProblemSource.HACKERRANK,
        "4": None
    }
    
    source = source_map.get(choice)
    if source not in source_map.values():
        print("Invalid choice!")
        return
    
    print("\nFetching random problem...")
    problem = fetcher.get_random_problem(source)
    
    if problem:
        print(f"\nFound Problem from {problem.source.value}:")
        print(f"Title: {problem.title}")
        print(f"Difficulty: {problem.difficulty}")
        print(f"Topics: {', '.join(problem.topics)}")
        
        workspace_dir = fetcher.setup_local_environment(problem)
        print(f"\nLocal workspace created at: {workspace_dir}")
        print("\nFiles created:")
        print(f"- {workspace_dir}/README.md (Problem description and notes)")
        print(f"- {workspace_dir}/solution.py (Python solution template)")
        print(f"- {workspace_dir}/solution.java (Java solution template)")
        print(f"- {workspace_dir}/solution.js (JavaScript solution template)")
        
        print("\nWould you like to:")
        print("1. Open the problem in your browser")
        print("2. Get another random problem")
        print("3. Exit")
        
        action = input("\nEnter your choice (1-3): ")
        
        if action == "1":
            import webbrowser
            webbrowser.open(problem.url)
        elif action == "2":
            main()
    else:
        print("Failed to fetch problem. Please try again.")

if __name__ == "__main__":
    main()