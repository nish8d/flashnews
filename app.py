import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add news_pipeline directory to path
sys.path.insert(0, str(Path(__file__).parent / "news_pipeline"))

from main import get_all_news

# Page configuration
st.set_page_config(
    page_title="News",
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
st.markdown('<div class="main-header">News past 24</div>', unsafe_allow_html=True)
# st.markdown("### Intelligent news collection from multiple sources with AI-powered deduplication")

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
                
                # Store results in session state
                st.session_state.results = results
                st.session_state.keyword_searched = keyword
                
                progress_bar.progress(100)
                progress_text.empty()
                progress_bar.empty()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Display results if they exist in session state
if st.session_state.results is not None:
    results = st.session_state.results
    keyword = st.session_state.keyword_searched
    
    # Display results
    st.success(f"Found {len(results)} relevant articles")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", len(results))
    with col2:
        sources = len(set(a['source'] for a in results))
        st.metric("Unique Sources", sources)
    with col3:
        avg_score = sum(a['score'] for a in results) / len(results) if results else 0
        st.metric("Avg Score", f"{avg_score:.2f}")
    with col4:
        high_quality = sum(1 for a in results if a['score'] >= 0.7)
        st.metric("High Quality", high_quality)
    
    st.markdown("---")
    
    # Filter and sort options
    col1, col2 = st.columns([2, 1])
    with col1:
        source_filter = st.multiselect(
            "Filter by source:",
            options=sorted(set(a['source'] for a in results)),
            default=[]
        )
    with col2:
        sort_order = st.selectbox(
            "Sort by:",
            options=["Relevance Score (High to Low)", "Relevance Score (Low to High)"],
            index=0
        )
    
    # Apply filters
    filtered_results = results
    if source_filter:
        filtered_results = [a for a in results if a['source'] in source_filter]
    
    # Apply sorting
    if "Low to High" in sort_order:
        filtered_results = sorted(filtered_results, key=lambda x: x['score'])
    else:
        filtered_results = sorted(filtered_results, key=lambda x: x['score'], reverse=True)
    
    st.markdown(f"Showing {len(filtered_results)} articles")
    
    # Display articles
    for idx, article in enumerate(filtered_results, 1):
        score = article['score']
        
        # Determine score class
        if score >= 0.7:
            score_class = "score-high"
        elif score >= 0.4:
            score_class = "score-medium"
        else:
            score_class = "score-low"
        
        with st.container():
            st.markdown(f"""
            <div class="article-card">
                <div class="article-title">{idx}. {article['title']}</div>
                <div class="article-meta">
                    <strong>Source:</strong> {article['source']} | 
                    <span class="score-badge {score_class}">Score: {score:.3f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if article.get('description'):
                    st.markdown(f"**Description:** {article['description']}")
            with col2:
                st.link_button("Read More", article['link'], use_container_width=True)
            
            st.markdown("---")
    
    # Export option
    if st.button("Export Results to CSV"):
        df = pd.DataFrame(results)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"news_results_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7f8c8d; padding: 2rem;'>"
    "Built with Streamlit | AI-Powered News Aggregation"
    "</div>",
    unsafe_allow_html=True
)