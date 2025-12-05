from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma

class ArticleRetriever:

    def __init__(self, persist_directory="vectordb"):
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db = Chroma(
            collection_name="news",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

    def add_articles(self, articles):
        texts = [article["content"] for article in articles]
        self.db.add_texts(texts)

    def search(self, query, k=2):
        return self.db.similarity_search(query, k=k)
