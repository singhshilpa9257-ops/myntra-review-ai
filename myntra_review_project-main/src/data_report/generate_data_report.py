import streamlit as st
import pandas as pd
import plotly.express as px
from src.ai_analyzer import AIAnalyzer

class DashboardGenerator:
    def __init__(self, data):
        self.data = data.copy()
        self.ai = AIAnalyzer()
        
        # Clean data types
        self.data['Rating'] = pd.to_numeric(self.data['Rating'], errors='coerce')
        self.data['Over_All_Rating'] = pd.to_numeric(self.data['Over_All_Rating'], errors='coerce')
        self.data['Price'] = self.data['Price'].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()
        self.data['Price'] = pd.to_numeric(self.data['Price'], errors='coerce')
        
        # Run sentiment analysis
        self.data = self.ai.analyze_sentiment(self.data)

    def display_general_info(self):
        st.header('General Information')
        
        st.subheader("🤖 AI-Powered Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Sentiment' in self.data.columns and not self.data['Sentiment'].empty:
                sentiment_counts = self.data['Sentiment'].value_counts()
                fig = px.pie(names=sentiment_counts.index, 
                           values=sentiment_counts.values, 
                           title="Overall Sentiment")
                st.plotly_chart(fig)
            else:
                st.write("Sentiment data not available yet.")
        
        with col2:
            avg_sentiment = self.data['Sentiment_Score'].mean() if 'Sentiment_Score' in self.data.columns else 0
            st.metric("Average Sentiment Score", f"{avg_sentiment:.2f}", 
                     delta="Positive" if avg_sentiment > 0 else "Negative")

        insights = self.ai.extract_key_insights(self.data)
        st.subheader("🔍 Key Themes")
        st.write("**Praises:**", ", ".join(insights.get('top_praises', [])))
        st.write("**Common Issues:**", ", ".join(insights.get('common_issues', [])))

    def display_product_sections(self):
        st.header('Product-wise Analysis')
        product_names = self.data['Product Name'].unique()
        
        for product_name in product_names:
            product_data = self.data[self.data['Product Name'] == product_name]
            
            st.subheader(f"📦 {product_name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_price = product_data['Price'].mean()
                st.metric("💰 Avg Price", f"₹{avg_price:.2f}" if pd.notna(avg_price) else "N/A")
            with col2:
                avg_rating = product_data['Over_All_Rating'].mean()
                st.metric("⭐ Avg Rating", f"{avg_rating:.2f}/5" if pd.notna(avg_rating) else "N/A")
            with col3:
                st.metric("Total Reviews", len(product_data))
            
            st.write("**Top Positive Reviews**")
            positive = product_data.nlargest(3, 'Rating')
            for _, row in positive.iterrows():
                st.write(f"⭐ **{row['Rating']}** - {str(row['Comment'])[:150]}...")
            
            st.write("**Common Complaints**")
            negative = product_data.nsmallest(3, 'Rating')
            for _, row in negative.iterrows():
                st.write(f"💢 **{row['Rating']}** - {str(row['Comment'])[:150]}...")
            
            st.divider()