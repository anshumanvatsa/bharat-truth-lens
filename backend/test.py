# quick_test.py — in backend folder
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.services.analyzer import wikipedia_search, tavily_search, extract_entity

tests = [
    "Aristotle spent time in Athens",
    "Magic Johnson did not play for the Lakers",
    "Tim Roth is an English actor",
]

for claim in tests:
    entity = extract_entity(claim)
    wiki   = wikipedia_search(claim)
    tavily = tavily_search(claim)
    print(f"\nClaim  : {claim}")
    print(f"Entity : {entity}")
    print(f"Wiki   : {len(wiki)} | Tavily: {len(tavily)}")
    if wiki:
        print(f"  → {wiki[0]['title']}: {wiki[0]['content'][:120]}...")