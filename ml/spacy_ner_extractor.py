# backend/ml/spacy_ner_extractor.py
# Replaces the rule-based entity extractor in HybridFact
# Install: pip install spacy && python -m spacy download en_core_web_lg

import spacy
import re
from typing import Optional

# Priority order for entity types most useful for FEVER claims
PRIORITY_ENTITY_TYPES = ["PERSON", "ORG", "GPE", "LOC", "WORK_OF_ART", "EVENT", "FAC", "PRODUCT"]

_nlp = None  # lazy load — only load once

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_lg")
        except OSError:
            # fallback to smaller model if lg not installed
            try:
                _nlp = spacy.load("en_core_web_sm")
                print("[NER] Warning: en_core_web_lg not found, using en_core_web_sm")
            except OSError:
                raise OSError(
                    "No spaCy model found. Run: python -m spacy download en_core_web_lg"
                )
    return _nlp


def extract_entity_spacy(claim: str) -> str:
    """
    Extract the primary searchable entity from a claim using spaCy NER.
    Falls back gracefully through multiple strategies.

    Args:
        claim: Raw claim string from FEVER or user input

    Returns:
        Best entity string for Wikipedia/Tavily search
    """
    nlp = _get_nlp()
    doc = nlp(claim)

    # Strategy 1: Find highest-priority named entity
    for priority_type in PRIORITY_ENTITY_TYPES:
        for ent in doc.ents:
            if ent.label_ == priority_type:
                entity = ent.text.strip()
                if len(entity) > 1:  # avoid single-char noise
                    return entity

    # Strategy 2: Any named entity at all
    if doc.ents:
        # Return the longest entity (usually most specific)
        best = max(doc.ents, key=lambda e: len(e.text))
        if len(best.text.strip()) > 1:
            return best.text.strip()

    # Strategy 3: Noun chunks (for claims without named entities)
    noun_chunks = list(doc.noun_chunks)
    if noun_chunks:
        # Filter out pronouns and very short chunks
        filtered = [
            chunk for chunk in noun_chunks
            if len(chunk.text.strip()) > 2
            and chunk.root.pos_ not in ("PRON",)
        ]
        if filtered:
            return filtered[0].text.strip()

    # Strategy 4: Original rule-based fallback (last resort)
    return _rule_based_fallback(claim)


def _rule_based_fallback(claim: str) -> str:
    """
    Original HybridFact rule-based extractor as final fallback.
    Only used when spaCy finds nothing useful.
    """
    # Lowercase normalize, strip articles, grab leading caps
    normalized = claim.lower()
    for article in ["the ", "a ", "an "]:
        if normalized.startswith(article):
            normalized = normalized[len(article):]

    # Grab first sequence of title-cased words from original
    tokens = claim.split()
    entity_tokens = []
    for token in tokens:
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", token)
        if clean and (clean[0].isupper() or entity_tokens):
            entity_tokens.append(clean)
            if len(entity_tokens) >= 3:
                break
        elif entity_tokens:
            break

    if entity_tokens:
        return " ".join(entity_tokens)

    # Absolute last resort: first 3 words
    return " ".join(claim.split()[:3])


def extract_entity_with_fallback_info(claim: str) -> dict:
    """
    Extended version that returns extraction metadata for logging/debugging.
    Useful for error analysis in the paper.
    """
    nlp = _get_nlp()
    doc = nlp(claim)

    result = {
        "entity": None,
        "method": None,
        "entity_type": None,
        "all_entities": [(ent.text, ent.label_) for ent in doc.ents]
    }

    # Strategy 1: Priority entity types
    for priority_type in PRIORITY_ENTITY_TYPES:
        for ent in doc.ents:
            if ent.label_ == priority_type:
                if len(ent.text.strip()) > 1:
                    result["entity"] = ent.text.strip()
                    result["method"] = "spacy_priority_ner"
                    result["entity_type"] = priority_type
                    return result

    # Strategy 2: Any entity
    if doc.ents:
        best = max(doc.ents, key=lambda e: len(e.text))
        if len(best.text.strip()) > 1:
            result["entity"] = best.text.strip()
            result["method"] = "spacy_any_ner"
            result["entity_type"] = best.label_
            return result

    # Strategy 3: Noun chunks
    noun_chunks = list(doc.noun_chunks)
    filtered = [c for c in noun_chunks if len(c.text.strip()) > 2 and c.root.pos_ != "PRON"]
    if filtered:
        result["entity"] = filtered[0].text.strip()
        result["method"] = "noun_chunk"
        result["entity_type"] = "NOUN_CHUNK"
        return result

    # Fallback
    result["entity"] = _rule_based_fallback(claim)
    result["method"] = "rule_based_fallback"
    result["entity_type"] = "UNKNOWN"
    return result


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_claims = [
        "Marie Curie was born in Warsaw",
        "According to research by Marie Curie the element was discovered",  # old extractor fails this
        "Magic Johnson did not play for the Lakers",
        "Arizona is a state in the United States",
        "The film was released in 1994",
        "Obamacare is a government takeover of healthcare",  # abstract political claim
        "The Eiffel Tower is located in Berlin",
    ]

    print("SpaCy NER Extraction Test")
    print("=" * 60)
    for claim in test_claims:
        info = extract_entity_with_fallback_info(claim)
        print(f"\nClaim : {claim}")
        print(f"Entity: {info['entity']}  [{info['entity_type']}]  via {info['method']}")
        print(f"All NEs found: {info['all_entities']}")