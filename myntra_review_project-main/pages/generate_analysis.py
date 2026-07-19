import pandas as pd
import streamlit as st 
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.data_report.generate_data_report import DashboardGenerator

mongo_con = MongoIO()

def create_analysis_page(review_data: pd.DataFrame):
    if review_data is not None and not review_data.empty:
        st.success(f"✅ {len(review_data)} reviews loaded!")

        # Convert Rating to numeric
        review_data['Rating'] = pd.to_numeric(review_data['Rating'], errors='coerce')

        st.dataframe(review_data.head(10))

        if st.button("Generate Analysis"):
            with st.spinner("Generating AI Analysis..."):
                dashboard = DashboardGenerator(review_data)
                dashboard.display_general_info()
                dashboard.display_product_sections()
    else:
        st.warning("No data available for this product.")

# Main Page Logic
try:
    if st.session_state.get("data", False) and st.session_state.get(SESSION_PRODUCT_KEY):
        product_name = st.session_state[SESSION_PRODUCT_KEY]
        data = mongo_con.get_reviews(product_name=product_name)
        
        create_analysis_page(data)
    else:
        st.markdown("### No Data Available for analysis.")
        st.info("Pehle 'Search Products' page pe jaakar reviews scrape karo.")
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Kuch product scrape karke try karo.")