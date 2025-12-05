from pydantic import BaseModel, ConfigDict
from typing import List

class Flashcard(BaseModel):
    model_config = ConfigDict(extra='forbid')

    title: str
    question: str
    answer: str
    score: str
    context: str
    the_company_mainly_concerned_with_the_news_article: str
    link: str
    source: str
    summary: str
    published_at: str

class FlashcardOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')

    flashcards: List[Flashcard]
