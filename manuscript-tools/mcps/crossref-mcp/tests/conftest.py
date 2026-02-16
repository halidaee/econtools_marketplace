import pytest

# Test data for Conley Udry pineapple paper
SEARCH_RESPONSE = {
    "status": "ok",
    "message-type": "work-list",
    "message-version": "1.0.0",
    "message": {
        "facets": {},
        "total-results": 1,
        "items": [
            {
                "indexed": {"date-parts": [[2025, 1, 15]], "date-time": "2025-01-15T09:00:00Z"},
                "reference-count": 42,
                "publisher": "American Economic Association",
                "title": ["Learning about a New Technology: Pineapple in Ghana"],
                "author": [
                    {"given": "Timothy G.", "family": "Conley"},
                    {"given": "Christopher R.", "family": "Udry"},
                ],
                "container-title": ["American Economic Review"],
                "type": "journal-article",
                "published": {"date-parts": [[2010, 1, 1]]},
                "DOI": "10.1257/aer.100.1.35",
                "volume": "100",
                "issue": "1",
                "page": "35-69",
            }
        ],
    },
}

SEARCH_EMPTY_RESPONSE = {
    "status": "ok",
    "message-type": "work-list",
    "message-version": "1.0.0",
    "message": {"facets": {}, "total-results": 0, "items": []},
}

GET_METADATA_RESPONSE = {
    "status": "ok",
    "message-type": "work",
    "message-version": "1.0.0",
    "message": {
        "indexed": {"date-parts": [[2025, 1, 15]], "date-time": "2025-01-15T09:00:00Z"},
        "reference-count": 42,
        "publisher": "American Economic Association",
        "title": ["Learning about a New Technology: Pineapple in Ghana"],
        "author": [
            {"given": "Timothy G.", "family": "Conley"},
            {"given": "Christopher R.", "family": "Udry"},
        ],
        "container-title": ["American Economic Review"],
        "type": "journal-article",
        "published": {"date-parts": [[2010, 1, 1]]},
        "DOI": "10.1257/aer.100.1.35",
        "volume": "100",
        "issue": "1",
        "page": "35-69",
        "abstract": "We study social learning about agricultural technology...",
    },
}

CONLEY_BIBTEX = (
    "@article{Conley2010LearningAA,\n"
    " title={Learning about a New Technology: Pineapple in Ghana},\n"
    " author={Timothy G. Conley and Christopher R. Udry},\n"
    " journal={American Economic Review},\n"
    " year={2010},\n"
    " volume={100},\n"
    " pages={35-69}\n"
    "}"
)
