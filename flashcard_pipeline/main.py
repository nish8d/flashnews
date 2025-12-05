# flashcard_pipeline/main.py

import os
import json
from dotenv import load_dotenv
from flashcard_pipeline.flashcard_generator import FlashcardGenerator

load_dotenv()  # loads .env from ROOT

# Path to the news output JSON in root directory
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
NEWS_JSON_PATH = os.path.join(ROOT_DIR, "resultsgen.json")
FLASHCARDS_JSON_PATH = os.path.join(ROOT_DIR, "flashcards.json")


def load_news_json():
    """Load the list of articles from resultsgen.json."""
    if not os.path.exists(NEWS_JSON_PATH):
        raise FileNotFoundError(f"❌ News JSON not found at: {NEWS_JSON_PATH}")

    with open(NEWS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Your JSON is a LIST of articles
    if not isinstance(data, list):
        raise ValueError("❌ Expected JSON to be a list of articles but got something else.")

    return data


def save_flashcards(data):
    """Write generated flashcards to flashcards.json."""
    with open(FLASHCARDS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Flashcards saved: {FLASHCARDS_JSON_PATH}")


def main():
    print("🚀 Flashcard pipeline started...\n")

    print("📄 Loading resultsgen.json ...")
    articles = load_news_json()
    print(f"📰 Found {len(articles)} articles.\n")

    generator = FlashcardGenerator()
    flashcard_results = []

    for idx, article in enumerate(articles, start=1):
        title = article.get("title", "Untitled Article")

        print(f"✨ Generating flashcards {idx}/{len(articles)} → {title}")

        # The model needs content — combine title + summary for best results
        article_payload = {
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "published_at": article.get("published_at", ""),
            "source": article.get("source", ""),
        }

        try:
            result = generator.generate_for_article(article_payload)
            flashcard_results.append(result.dict())

        except Exception as e:
            print(f"⚠ Error generating flashcards for article {idx}: {e}")

    save_flashcards(flashcard_results)

    print("\n🎉 Flashcard pipeline finished successfully!")


if __name__ == "__main__":
    main()
