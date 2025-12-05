FLASHCARD_PROMPT = """
You are an AI flashcard generator.

Convert this news article into educational flashcards.
Include:
    title
    question
    answer
    context
    the_company_mainly_concerned_with_the_news_article
    link
    source
    summary
    published_at

Use only information from the article. No hallucinations.

ARTICLE:
{article}
"""
