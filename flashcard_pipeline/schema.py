from pydantic import BaseModel
from typing import List

class Flashcard(BaseModel):
    question: str
    answer: str
    difficulty: str
    topic: str
    context: str

    title: str
    the_company_mainly_concerned_with_the_news_article: str
    link: str
    source: str
    summary: str
    published_at: str
    score: str

class FlashcardOutput(BaseModel):
    flashcards: List[Flashcard]
