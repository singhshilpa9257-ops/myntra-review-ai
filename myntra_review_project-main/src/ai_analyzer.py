# src/ai_analyzer.py
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import openai
import os
from src.exception import CustomException
import sys

class AIAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        except:
            self.sentiment_pipeline = None

    def analyze_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add sentiment scores to dataframe"""
        def get_vader_score(text):
            scores = self.vader.polarity_scores(str(text))
            return scores['compound']
        
        df = df.copy()
        df['Sentiment_Score'] = df['Comment'].apply(get_vader_score)
        df['Sentiment'] = df['Sentiment_Score'].apply(
            lambda x: 'Positive' if x > 0.05 else 'Negative' if x < -0.05 else 'Neutral'
        )
        return df

    def generate_summary(self, comments: list, max_length=200) -> str:
        """Generate AI summary using OpenAI/Grok"""
        try:
            comments_text = "\n".join(comments[:50])  # limit for cost/speed
            
            prompt = f"""Summarize the following customer reviews for a fashion product. 
            Highlight common praises, complaints, quality, fit, and overall sentiment:

            {comments_text}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or groq/mixtral
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return "AI Summary unavailable. " + str(e)

    def extract_key_insights(self, df: pd.DataFrame) -> dict:
        """Generate key insights"""
        insights = {}
        
        # Common themes (simple keyword approach)
        positive_keywords = ['good', 'great', 'excellent', 'comfortable', 'quality', 'soft', 'perfect']
        negative_keywords = ['bad', 'poor', 'small', 'large', 'thin', 'transparent', 'shrink']
        
        all_text = " ".join(df['Comment'].astype(str)).lower()
        
        insights['top_praises'] = [kw for kw in positive_keywords if kw in all_text]
        insights['common_issues'] = [kw for kw in negative_keywords if kw in all_text]
        
        return insights