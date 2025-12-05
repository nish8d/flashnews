import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from .prompts import FLASHCARD_PROMPT
from .schema import FlashcardOutput

class FlashcardGenerator:

    def __init__(self):
        self.llm = ChatOllama(
            model="mistral",
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(FLASHCARD_PROMPT)

    def load_news(self, file_path="news_output.json"):
        with open(file_path, "r") as f:
            return json.load(f)

    def generate_for_article(self, article):
        chain = self.prompt | self.llm.with_structured_output(FlashcardOutput)
        return chain.invoke({"article": article})

    def run(self, output_file="flashcards.json"):
        news_data = self.load_news()
        flashcards = []

        for article in news_data["articles"]:
            result = self.generate_for_article(article)
            flashcards.append(result)

        with open(output_file, "w") as f:
            json.dump(flashcards, f, indent=4)

        print("Flashcards generated:", output_file)
