from typing import TypedDict


class ReviewState(TypedDict):
    article: str
    style_guide: str

    grammar_score: float
    grammar_feedback: str

    seo_score: float
    seo_feedback: str

    readability_score: float
    readability_feedback: str

    seo_titles: str
    meta_description: str
    improved_article: str