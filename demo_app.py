"""
Interactive Demo for E-Commerce Session-Based Recommender System
Run with: streamlit run demo_app.py
"""
import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime
import random

# Configuration
API_URL = st.sidebar.text_input("API URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Session-Based Recommender Demo",
    page_icon="🛍️",
    layout="wide"
)

# Title
st.title("🛍️ E-Commerce Session-Based Recommender System")
st.markdown("**Interactive Demo** - See real-time product recommendations based on your browsing behavior")

# Sidebar - Session Info
st.sidebar.header("📊 Session Information")
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"demo_session_{int(time.time())}"
    st.session_state.events = []
    st.session_state.recommendations = []

st.sidebar.info(f"**Session ID:** `{st.session_state.session_id}`")
st.sidebar.metric("Events Tracked", len(st.session_state.events))

# Sample products
SAMPLE_PRODUCTS = {
    "prod_001": {"name": "Wireless Headphones", "category": "Electronics", "price": 79.99},
    "prod_002": {"name": "Coffee Maker", "category": "Home & Kitchen", "price": 129.99},
    "prod_003": {"name": "Running Shoes", "category": "Sports", "price": 89.99},
    "prod_004": {"name": "Laptop Stand", "category": "Electronics", "price": 39.99},
    "prod_005": {"name": "Yoga Mat", "category": "Sports", "price": 24.99},
    "prod_006": {"name": "Desk Lamp", "category": "Home & Kitchen", "price": 34.99},
    "prod_007": {"name": "Bluetooth Speaker", "category": "Electronics", "price": 59.99},
    "prod_008": {"name": "Water Bottle", "category": "Sports", "price": 19.99},
    "prod_009": {"name": "Kitchen Knife Set", "category": "Home & Kitchen", "price": 149.99},
    "prod_010": {"name": "USB-C Cable", "category": "Electronics", "price": 12.99},
}

# Check API Health
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Track Event
def track_event(item_id, event_type):
    try:
        payload = {
            "session_id": st.session_state.session_id,
            "item_id": item_id,
            "event_type": event_type,
            "metadata": SAMPLE_PRODUCTS.get(item_id, {})
        }
        response = requests.post(f"{API_URL}/event", json=payload, timeout=2)
        if response.status_code == 200:
            st.session_state.events.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "item": SAMPLE_PRODUCTS[item_id]["name"],
                "event": event_type
            })
            return True
    except Exception as e:
        st.error(f"Error tracking event: {e}")
    return False

# Get Recommendations
def get_recommendations(k=10):
    try:
        payload = {
            "session_id": st.session_state.session_id,
            "k": k
        }
        response = requests.post(f"{API_URL}/recommend", json=payload, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
    return None

# API Status
api_status = check_api_health()
if api_status:
    st.sidebar.success("✅ API Connected")
else:
    st.sidebar.error("❌ API Offline")
    st.error("⚠️ API is not running. Start the API with: `docker compose up` or `uvicorn src.api.main:app`")

# Main sections
tab1, tab2, tab3, tab4 = st.tabs(["🛒 Browse Products", "⭐ Recommendations", "📈 Session History", "ℹ️ How It Works"])

# Tab 1: Browse Products
with tab1:
    st.header("Browse Products")
    st.markdown("Click on products to simulate different user interactions")
    
    cols = st.columns(3)
    for idx, (prod_id, prod_info) in enumerate(SAMPLE_PRODUCTS.items()):
        with cols[idx % 3]:
            st.subheader(prod_info["name"])
            st.caption(f"Category: {prod_info['category']}")
            st.write(f"💰 ${prod_info['price']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👁️ View", key=f"view_{prod_id}"):
                    if track_event(prod_id, "view"):
                        st.success("Viewed!")
            with col2:
                if st.button("🖱️ Click", key=f"click_{prod_id}"):
                    if track_event(prod_id, "click"):
                        st.success("Clicked!")
            with col3:
                if st.button("🛒 Add", key=f"cart_{prod_id}"):
                    if track_event(prod_id, "add_to_cart"):
                        st.success("Added!")
            st.divider()

# Tab 2: Recommendations
with tab2:
    st.header("Get Personalized Recommendations")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Based on your current session activity, here are the recommended products:")
    with col2:
        num_recs = st.slider("Number of recommendations", 5, 20, 10)
    
    if st.button("🔄 Get Recommendations", type="primary"):
        if not api_status:
            st.error("API is offline. Cannot get recommendations.")
        elif len(st.session_state.events) == 0:
            st.warning("Browse some products first to get personalized recommendations!")
        else:
            with st.spinner("Generating recommendations..."):
                result = get_recommendations(k=num_recs)
                if result:
                    st.session_state.recommendations = result
    
    if st.session_state.recommendations:
        recs = st.session_state.recommendations
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Recommendations", len(recs.get('recommendations', [])))
        with col2:
            st.metric("Latency", f"{recs.get('latency_ms', 0):.1f} ms")
        with col3:
            st.metric("Model Version", recs.get('model_version', 'N/A'))
        
        st.subheader("📋 Recommended Products")
        
        # Display recommendations
        rec_data = []
        for rec in recs.get('recommendations', []):
            item_id = rec['item_id']
            if item_id in SAMPLE_PRODUCTS:
                prod = SAMPLE_PRODUCTS[item_id]
                rec_data.append({
                    "Rank": rec['rank'],
                    "Product": prod['name'],
                    "Category": prod['category'],
                    "Price": f"${prod['price']}",
                    "Score": f"{rec['score']:.3f}",
                    "Reason": rec['reason']
                })
            else:
                rec_data.append({
                    "Rank": rec['rank'],
                    "Product": item_id,
                    "Category": "Unknown",
                    "Price": "N/A",
                    "Score": f"{rec['score']:.3f}",
                    "Reason": rec['reason']
                })
        
        if rec_data:
            df = pd.DataFrame(rec_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            st.subheader("📊 Recommendation Scores")
            chart_data = pd.DataFrame({
                'Product': [r['Product'] for r in rec_data[:10]],
                'Score': [float(r['Score']) for r in rec_data[:10]]
            })
            st.bar_chart(chart_data.set_index('Product'))

# Tab 3: Session History
with tab3:
    st.header("Session Activity Timeline")
    
    if st.session_state.events:
        # Event statistics
        col1, col2, col3, col4 = st.columns(4)
        event_counts = pd.DataFrame(st.session_state.events)['event'].value_counts()
        
        with col1:
            st.metric("👁️ Views", event_counts.get('view', 0))
        with col2:
            st.metric("🖱️ Clicks", event_counts.get('click', 0))
        with col3:
            st.metric("🛒 Add to Cart", event_counts.get('add_to_cart', 0))
        with col4:
            st.metric("💳 Purchases", event_counts.get('purchase', 0))
        
        st.subheader("Event Timeline")
        events_df = pd.DataFrame(st.session_state.events)
        events_df = events_df.rename(columns={
            'time': 'Time',
            'item': 'Product',
            'event': 'Event Type'
        })
        st.dataframe(events_df, use_container_width=True, hide_index=True)
        
        # Clear session button
        if st.button("🗑️ Clear Session", type="secondary"):
            st.session_state.session_id = f"demo_session_{int(time.time())}"
            st.session_state.events = []
            st.session_state.recommendations = []
            st.rerun()
    else:
        st.info("No events tracked yet. Start browsing products!")

# Tab 4: How It Works
with tab4:
    st.header("How the Recommendation System Works")
    
    st.markdown("""
    ### 🎯 Architecture Overview
    
    This is a **session-based recommendation system** that provides real-time product suggestions based on user behavior within a single session.
    
    #### Components:
    
    1. **Event Tracking** 
       - Captures user interactions (views, clicks, add-to-cart)
       - Stores session state in Redis for fast access
       
    2. **Candidate Generation**
       - Retrieves similar items using item-to-item collaborative filtering
       - Includes popular items as fallback
       - Generates ~100 candidate products
    
    3. **Ranking with LightGBM**
       - Scores each candidate using machine learning
       - Features: item popularity, session context, similarity scores
       - Returns top-K items with highest scores
    
    4. **Real-time Response**
       - P95 latency < 50ms
       - Session state persists for 24 hours
    
    ### 📊 Model Performance
    
    - **Recall@20**: 0.52 (52% of relevant items found in top 20)
    - **NDCG@10**: 0.42 (ranking quality score)
    - **MAP@20**: 0.35 (mean average precision)
    
    ### 🔧 Key Features
    
    - ⚡ Real-time recommendations
    - 🎯 No user history required (cold-start friendly)
    - 🤖 ML-powered ranking
    - 🔄 Redis-backed session management
    - 🐳 Docker-ready deployment
    
    ### 📚 Learn More
    
    - [GitHub Repository](https://github.com/Pavan-r-m/ecommerce-session-recsys)
    - [API Documentation](http://localhost:8000/docs)
    """)
    
    st.subheader("🚀 Try It Yourself")
    st.code("""
# Start the API
docker compose up

# Run this demo
streamlit run demo_app.py

# Or use the API directly
curl -X POST http://localhost:8000/event \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "test_123",
    "item_id": "prod_001",
    "event_type": "view"
  }'
    """, language="bash")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center'>
    <p><strong>E-Commerce Session-Based Recommender System</strong></p>
    <p>Built with FastAPI, Redis, LightGBM, and Streamlit</p>
    <p><a href='https://github.com/Pavan-r-m/ecommerce-session-recsys'>⭐ Star on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
