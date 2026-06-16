import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the brains we built in Phase 2
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(page_title="TTB Label Verifier (Demo)", layout="wide")

# 2. Inject Official Government Header, Logos & Test Disclaimer
st.markdown("""
<style>
    /* Import official USWDS font */
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap');
    
    /* Apply font and force square corners on all containers */
    html, body, [class*="css"] {
        font-family: 'Public Sans', sans-serif !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 0px !important;
    }
</style>

<div style='background-color: #f0f0f0; color: #1b1b1b; padding: 4px 20px; font-size: 12px; display: flex; align-items: center; border-bottom: 1px solid #dfe1e2;'>
    <img src="https://upload.wikimedia.org/wikipedia/en/a/a4/Flag_of_the_United_States.svg" width="16" height="11" style="margin-right: 8px;" alt="US Flag">
    <span>An official demonstration prototype of the United States Government</span>
</div>

<div style='background-color: #fac22b; color: #1b1b1b; padding: 10px 20px; font-size: 14px; font-weight: bold; text-align: center; border-bottom: 2px solid #1a1a1a;'>
    DEMONSTRATION PROTOTYPE: Built solely for technical interview assessment. Not an official TTB tool.
</div>

<div style='background-color: #005ea2; color: #ffffff; padding: 25px 20px; margin-bottom: 25px; border-bottom: 4px solid #1a1a1a; overflow: hidden;'>
    
    <svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="float:left; margin-right: 20px; margin-top: 2px;">
       <path d="M50 5 L10 25 L10 60 C10 80 50 95 50 95 C50 95 90 80 90 60 L90 25 Z" fill="none" stroke="#ffffff" stroke-width="6" stroke-linejoin="round"/>
       <circle cx="50" cy="45" r="18" fill="none" stroke="#ffffff" stroke-width="4"/>
       <rect x="35" y="70" width="30" height="4" fill="#ffffff"/>
       <path d="M50 27 L50 63" stroke="#ffffff" stroke-width="4"/>
       <path d="M32 45 L6

# 3. Layout: Split Screen with Material-style "Cards"
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
                st.image(uploaded_file, caption="Label Artwork Ready for Review", use_container_width=True)

with col2:
    # MATERIAL CARD 2: Audit Results Engine
    with st.container(border=True):
        st.subheader("3. Automated Verification Audit")
        st.caption("AI-powered discrepancy analysis.")
        
        if uploaded_file:
            if st.button("Run Automated Compliance Check", type="primary", use_container_width=True):
                
                with st.spinner("Analyzing image features and running logic rules... (Expected: < 5s)"):
                    try:
                        # Convert SVG to PNG for the AI engine
                        if uploaded_file.name.endswith('.svg'):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
                                f.write(uploaded_file.getvalue())
                                tmp_path = f.name
                            
                            drawing = svg2rlg(tmp_path)
                            png_io = io.BytesIO()
                            renderPM.drawToFile(drawing, png_io, fmt="PNG")
                            img = Image.open(png_io)
                        else:
                            img = Image.open(uploaded_file)
                        
                        # Step 1: Have the AI read the label
                        extracted_data = analyze_label_image(img)
                        
                        # Step 2: Bundle ALL the form data from the left column
                        form_data = {
                            "brand_name": app_brand,
                            "fanciful_name": app_fanciful,
                            "class_type": app_type,
                            "abv": app_abv,
                            "net_contents": app_net,
                            "bottler_info": app_bottler,
                            "appellation": app_appellation,
                            "vintage": app_vintage
                        }
                        
                        # Filter out empty fields
                        form_data = {k: v for k, v in form_data.items() if v.strip() != ""}
                        
                        # Step 3: Run the compliance engine
                        audit_results = verify_compliance(form_data, extracted_data)
                        
                        st.write("") 
                        
                        # Step 4: Display the Results
                        for element, data in audit_results.items():
                            with st.container(border=True):
                                st.markdown(f"#### {element.replace('_', ' ').title()}")
                                
                                if "PASS" in data["status"]:
                                    st.success(f"**STATUS: {data['status']}** ({data['confidence']})")
                                elif "REVIEW" in data["status"]:
                                    st.warning(f"**STATUS: {data['status']}** ({data['confidence']})")
                                else:
                                    st.error(f"**STATUS: {data['status']}** ({data['confidence']})")
                                    
                                metric_c1, metric_c2 = st.columns(2)
                                metric_c1.metric("Expected (Form Value)", data["form"])
                                metric_c2.metric("Extracted (From Label)", data["label"])
                            
                    except Exception as e:
                        st.error(f"An error occurred during verification processing: {e}")
                        st.info("Check your terminal to ensure your API key is correct and you have internet access.")
        else:
            st.info("Please enter the application data and upload a label image on the left to run the compliance engine.")
