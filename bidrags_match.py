
import json
import re
from collections import Counter
from typing import List, Tuple, Dict

def load_database(json_path: str) -> List[Dict]:
    """Load the grants database from a JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def tokenize(text: str) -> List[str]:
    """Tokenize the text into lowercase words."""
    return re.findall(r'\b\w+\b', text.lower())

def compute_match_scores(project_text: str, database: List[Dict]) -> List[Tuple[str, float]]:
    """
    Compute a simple match score for each grant based on keyword overlap.
    Returns a list of tuples (grant_name, score) sorted by score descending.
    """
    project_tokens = tokenize(project_text)
    project_counts = Counter(project_tokens)
    results = []
    for item in database:
        keywords = [kw.lower() for kw in item.get('nyckelord', [])]
        # count overlaps
        overlap = sum(project_counts.get(kw, 0) for kw in keywords)
        score = overlap / (len(keywords) + 1e-9)
        results.append((item['namn'], score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def suggest_rubrik(fond_name: str, project_title: str) -> str:
    """
    Generate a simple suggested title for the application based on the grant name and project title.
    """
    return f"{project_title} – ansökan till {fond_name}"

def main(project_text: str, project_title: str, db_path: str = 'BidragsAI_database_v1.json') -> Dict:
    database = load_database(db_path)
    matches = compute_match_scores(project_text, database)
    top_matches = []
    for name, score in matches[:3]:
        rubrik = suggest_rubrik(name, project_title)
        top_matches.append({
            'fond': name,
            'poäng': round(score, 2),
            'rubrikförslag': rubrik
        })
    return {
        'projekt': project_title,
        'matchningar': top_matches
    }

if __name__ == '__main__':
    # Example usage
    db = '/mnt/data/BidragsAI_database_v1.json'
    project_title = 'RymdenLive26 – Ljudstad Borås'
    project_text = (
        'RymdenLive26 är ett experimentellt elektroniskt musikprojekt i Borås med regional spridning. '
        'Projektet syftar till att skapa en hybrid konsertserie med VR-streaming och interaktiv teknik. '
        'Det riktar sig till nya publikgrupper och samverkar med regionala partners.'
    )
    result = main(project_text, project_title, db)
    print(result)
