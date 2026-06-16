import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the brains we built in Phase 2
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="Alcohol Label Verifier", layout="wide")

# Main Header
st.title("Alcohol Label Verifier")
st.markdown("Automated discrepancy detection between application records and bottle labels.")
st.write("") 

# 2. Layout: Split Screen with Material-style "Cards"
col1, col2 = st.columns([1, 1.5]) 

with col1:
    # MATERIAL CARD 1: Input Data
    with st.container(border=True):
        st.subheader("1. Government Label Data")
        
        st.info(
            "**Instructions:** Fill out the fields below exactly as they appear on your official "
            "COLA (Certification/Exemption of Label/Bottle Approval) application form. "
            "Once completed, upload the corresponding label artwork below to run the audit."
        )
        
        # Form Data inputs
        app_brand = st.text_input(
            "Brand Name", 
            help="Enter the brand name or producer exactly as written on the application."
        )
        app_fanciful = st.text_input(
            "Fanciful Name (Optional)", 
            help="An optional, descriptive name added to the label."
        )
        app_type = st.text_input(
            "Class/Type Designation", 
            help="e.g., 'Kentucky Straight Bourbon Whiskey', 'Red Wine', etc."
        )
        app_abv = st.text_input(
            "Alcohol Content (ABV)", 
            help="e.g., '45% Alc./Vol.' or '13.5% by Vol.'"
        )
        app_net = st.text_input(
            "Net Contents", 
            help="e.g., '750 mL' or '12 fl. oz.'"
        )
        app_bottler = st.text_input(
            "Name & Address of Bottler/Importer", 
            help="The mandated name and address statement."
        )
        
        # Expandable section for Wine-specific fields
        with st.expander("Additional Fields (Wine Specific)"):
            app_appellation = st.text_input(
                "Appellation of Origin", 
                help="Required for certain wines, indicates where the grapes were grown."
            )
            app_vintage = st.text_input(
                "Vintage Date", 
                help="The year the grapes were harvested."
            )
        
        st.divider() 
        
        st.subheader("2. Upload Label Artwork")
        uploaded_file = st.file_uploader("Choose a label image", type=["png", "jpg", "jpeg", "svg"])
        
        if uploaded_file:
            # Safely handle the image preview based on file type
            if uploaded_file.name.endswith('.svg'):
                # Render SVG directly as HTML
                svg_string = uploaded_file.getvalue().decode("utf-8")
                st.markdown(svg_string, unsafe_allow_html=True)
                st.caption("Label Artwork Ready for Review")
            else:
                # Standard images proceed normally
                st.image(uploaded_file, caption="Label Artwork Ready for Review", use_container
