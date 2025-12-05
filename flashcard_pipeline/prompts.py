FLASHCARD_PROMPT = """
You are an AI flashcard generator.

Convert this news article into educational flashcards.
Include:
    title
    question
    answer
    score
    context
    the_company_mainly_concerned_with_the_news_article
    link
    source = same as the scored mentioned in the json file
    summary
    published_at

Use only information from the article. No hallucinations.

ARTICLE:
{article}
"""
