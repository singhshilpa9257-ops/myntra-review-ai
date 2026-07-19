import streamlit as st
import pandas as pd
from src.cloud_io import MongoIO

st.title("💬 AI Review Assistant")

mongo = MongoIO()

# Get all products
try:
    collection_names = mongo.client[mongo.db.name].list_collection_names()
    product_options = [name.replace("_", " ") for name in collection_names if name]
except:
    product_options = []

if not product_options:
    st.warning("Koi product database mein nahi mila. Pehle reviews scrape karke store karo.")
    st.stop()

selected_product = st.selectbox("Select Product", options=product_options)

if selected_product:
    data = mongo.get_reviews(selected_product)
    
    if data.empty:
        st.error("No reviews found.")
    else:
        # 🔥 IMPORTANT: Convert Rating to numeric
        data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')
        
        st.success(f"✅ {len(data)} reviews loaded for **{selected_product}**")
        
        # Display basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Rating", f"{data['Rating'].mean():.2f}/5")
        with col2:
            st.metric("Total Reviews", len(data))
        with col3:
            positive = len(data[data['Rating'] >= 4])
            st.metric("Positive Reviews", positive)
        
        # AI Chat
        query = st.text_input("Reviews ke baare mein kya jaanna chahte ho? (e.g. quality, size, fit)")
        
        if query and st.button("Ask AI"):
            with st.spinner("AI soch raha hai..."):
                relevant = data[data['Comment'].str.contains(query, case=False, na=False)]
                
                if not relevant.empty:
                    st.subheader("Matching Reviews")
                    st.dataframe(relevant[['Name', 'Rating', 'Comment', 'Date']].head(10))
                else:
                    st.info("Exact match nahi mila. Yahan overall summary hai:")
                    st.write(f"**Average Rating:** {data['Rating'].mean():.2f}/5")
                    st.write(f"**Positive Reviews:** {len(data[data['Rating'] >= 4])}")
                    st.write(f"**Negative Reviews:** {len(data[data['Rating'] <= 2])}")
                    
                    # Top comments
                    st.subheader("Top Positive Comments")
                    positive_comments = data.nlargest(5, 'Rating')[['Rating', 'Comment']]
                    st.dataframe(positive_comments)