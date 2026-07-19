import pandas as pd
import streamlit as st 
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews

st.set_page_config("Myntra Review Scrapper")

st.title("Myntra Review Scrapper")

# Initialize session state
if "data" not in st.session_state:
    st.session_state["data"] = False
if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = ""

def form_input():
    product = st.text_input("Search Products", value=st.session_state[SESSION_PRODUCT_KEY])
    st.session_state[SESSION_PRODUCT_KEY] = product
    
    no_of_products = st.number_input("No of products to search", 
                                     step=1, min_value=1, value=1)

    if st.button("Scrape Reviews"):
        if not product.strip():
            st.error("Please enter a product name")
            return
            
        with st.spinner("Scraping reviews..."):
            scrapper = ScrapeReviews(
                product_name=product,
                no_of_products=int(no_of_products)
            )

            scrapped_data = scrapper.get_review_data()
            
            if scrapped_data is not None and not scrapped_data.empty:
                st.session_state["data"] = True
                mongoio = MongoIO()
                mongoio.store_reviews(product_name=product, reviews=scrapped_data)
                st.success("✅ Data scraped and stored successfully!")
                st.dataframe(scrapped_data)
            else:
                st.error("No data scraped. Try again.")

if __name__ == "__main__":
    form_input()