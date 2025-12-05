import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import json
import os

# Add pipeline directories to path (news_pipeline first to avoid import conflicts)
sys.path.insert(0, str(Path(__file__).parent / "flashcard_pipeline"))
sys.path.insert(0, str(Path(__file__).parent / "news_pipeline"))

# Import functions directly from modules
from news_pipeline.main import get_all_news
from flashcard_pipeline.main import main as run_flashcard_pipeline

# Page configuration
st.set_page_config(
    page_title="Flashcards",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1.5rem;
    }
    .article-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .article-meta {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .score-high {
        background-color: #d4edda;
        color: #155724;
    }
    .score-medium {
        background-color: #fff3cd;
        color: #856404;
    }
    .score-low {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">Flashcards from News</div>', unsafe_allow_html=True)
# st.markdown("### Generate educational flashcards from AI-powered news aggregation")

# Sidebar
with st.sidebar:
    st.header("Search Settings")
    
    keyword = st.text_input(
        "Enter search keyword/topic:",
        value="",
        help="Enter the topic or keyword you want to search for"
    )
    
    st.markdown("---")
    
    # Display information
    st.markdown("Features")
    st.markdown("""
    - Multi-source aggregation
    - Keyword relevance filtering
    - Semantic embeddings
    - AI-powered deduplication
    - Relevance scoring
    """)
    
    st.markdown("---")
    st.markdown("Data Sources")
    st.markdown("""
    - NewsData API
    - NewsAPI
    - GNews API
    """)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_button = st.button("Search News", type="primary", use_container_width=True)

# Initialize session state for results
if 'results' not in st.session_state:
    st.session_state.results = None
if 'keyword_searched' not in st.session_state:
    st.session_state.keyword_searched = None
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = None

# Results section
if search_button:
    if not keyword.strip():
        st.error("Please enter a search keyword")
    else:
        with st.spinner(f"Searching for '{keyword}'..."):
            try:
                # Create progress indicators
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                progress_text.text("Fetching articles from sources...")
                progress_bar.progress(20)
                
                results = get_all_news(keyword)

                # Remove embeddings — they are NumPy arrays, not JSON-serializable
                for article in results:
                    article.pop("embedding", None)

                # Save results to resultsgen.json
                with open("resultsgen.json", "w") as f:
                    json.dump(results, f, indent=2)

                # Run flashcard pipeline
                progress_text.text("Generating flashcards...")
                progress_bar.progress(60)
                run_flashcard_pipeline()
                progress_bar.progress(80)

                # Load flashcards
                with open("flashcards.json", "r") as f:
                    flashcards = json.load(f)

                # Store in session state
                st.session_state.results = results
                st.session_state.flashcards = flashcards
                st.session_state.keyword_searched = keyword

                progress_bar.progress(100)
                progress_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Display flashcards if they exist in session state
if st.session_state.flashcards is not None:
    flashcards = st.session_state.flashcards
    keyword = st.session_state.keyword_searched

    # Flatten flashcards list
    all_flashcards = []
    for article_flashcards in flashcards:
        all_flashcards.extend(article_flashcards['flashcards'])

    # Display results
    st.success(f"Generated {len(all_flashcards)} flashcards")

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Flashcards", len(all_flashcards))
    with col2:
        topics = len(set(f['topic'] for f in all_flashcards))
        st.metric("Unique Topics", topics)
    with col3:
        difficulties = ['easy', 'medium', 'hard']
        avg_diff = sum(difficulties.index(f['difficulty'].lower()) for f in all_flashcards) / len(all_flashcards) if all_flashcards else 0
        st.metric("Avg Difficulty", f"{avg_diff:.1f}")
    with col4:
        high_quality = sum(1 for f in all_flashcards if f['difficulty'].lower() == 'hard')
        st.metric("Advanced Cards", high_quality)

    st.markdown("---")

    # Filter and sort options
    col1, col2 = st.columns([2, 1])
    with col1:
        difficulty_filter = st.multiselect(
            "Filter by difficulty:",
            options=sorted(set(f['difficulty'] for f in all_flashcards)),
            default=[]
        )
    with col2:
        sort_order = st.selectbox(
            "Sort by:",
            options=["Difficulty (Easy to Hard)", "Difficulty (Hard to Easy)"],
            index=0
        )

    # Apply filters
    filtered_flashcards = all_flashcards
    if difficulty_filter:
        filtered_flashcards = [f for f in all_flashcards if f['difficulty'] in difficulty_filter]

    # Apply sorting
    if "Hard to Easy" in sort_order:
        filtered_flashcards = sorted(filtered_flashcards, key=lambda x: difficulties.index(x['difficulty'].lower()), reverse=True)
    else:
        filtered_flashcards = sorted(filtered_flashcards, key=lambda x: difficulties.index(x['difficulty'].lower()))

    st.markdown(f"Showing {len(filtered_flashcards)} flashcards")

    # Display flashcards
    for idx, flashcard in enumerate(filtered_flashcards, 1):
        with st.container():
            st.markdown(f"""
            <div class="article-card">
                <div class="article-title">{idx}. {flashcard['question']}</div>
                <div class="article-meta">
                    <strong>Answer:</strong> {flashcard['answer']} |
                    <strong>Difficulty:</strong> {flashcard['difficulty']} |
                    <strong>Topic:</strong> {flashcard['topic']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show article metadata
            with st.expander("Article Details"):
                st.markdown(f"**Title:** {flashcard['title']}")
                st.markdown(f"**Source:** {flashcard['source']}")
                st.markdown(f"**Published:** {flashcard['published_at']}")
                st.markdown(f"**Summary:** {flashcard['summary']}")
                st.markdown(f"**Score:** {flashcard['score']}")
                st.link_button("Read Full Article", flashcard['link'])

            st.markdown("---")

    # Export option
    if st.button("Export Flashcards to JSON"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(all_flashcards, indent=2),
            file_name=f"flashcards_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; padding: 2rem;'>"
    "Built with Streamlit | AI-Powered News Aggregation & Flashcard Generation"
    "</div>",
    unsafe_allow_html=True
)
