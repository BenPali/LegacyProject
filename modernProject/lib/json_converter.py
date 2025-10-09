import json
from typing import Any, Dict


def to_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def from_json(s: str) -> Dict:
    return json.loads(s)


def person_to_dict(person) -> Dict:
    return {
        "first_name": getattr(person, 'first_name', ''),
        "surname": getattr(person, 'surname', ''),
        "occ": getattr(person, 'occ', 0)
    }


def family_to_dict(family) -> Dict:
    return {
        "marriage": getattr(family, 'marriage', None),
        "relation": getattr(family, 'relation', None)
    }
