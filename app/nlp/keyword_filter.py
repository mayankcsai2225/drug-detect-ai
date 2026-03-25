from typing import Set

# A comprehensive set of drug-related keywords and Hinglish variants
DRUG_KEYWORDS: Set[str] = frozenset({
    # Common Drug Names
    'mdma', 'molly', 'ecstasy', 'lsd', 'acid', 'tabs', 'mephedrone', 'meow', 
    'crystal meth', 'ice', 'smack', 'brown sugar', 'ganja', 'charas', 'mandrax', 
    'ketamine', 'nitrazepam', 'alprazolam', 'xanax', 'weed', 'coke', 'charlie', 
    'snow', 'special k', 'ghb', 'rohypnol', 'fentanyl', 'tramadol', 'codeine syrup', 
    'lean', 'heroin', 'opium', 'amphetamine', 'shrooms', 'psilocybin', 'dmt', 
    'hashish', 'pot', 'marijuana', 'bud', 'kush', 'pills', 'speed', 'base',

    # Slang and Street Terms
    'plug', 'score', 'g', 'whizz', 'blow', 'lines', 'bags', 'stashed', 're-up',
    'vendor', 'darknet', 'stealth', 'drop', 'pickup', 'runner',

    # Hinglish Variants & Local Code Names
    'maal', 'chaabi', 'parcel', 'delivery', 'ghanta', 'bhai connect', 
    'cash on delivery', 'cod available', 'bhole', 'shakti', 'green tea', 
    'medicine', 'puchka', 'ghoda', 'bamb', 'full power', 'psy', 'trippy'
})

def check_keywords(text: str) -> bool:
    """
    Checks if any drug-related keywords exist in the text using fast set intersection.
    Returns True if a match is found, False otherwise.
    """
    if not text:
        return False
    
    # Tokenize and normalize text
    tokens = set(text.lower().split())
    
    # Return True if there's any intersection
    return bool(tokens & DRUG_KEYWORDS)

def get_matched_keywords(text: str) -> Set[str]:
    """
    Returns the set of keywords that matched in the text.
    """
    if not text:
        return set()
    
    tokens = set(text.lower().split())
    return tokens & DRUG_KEYWORDS
