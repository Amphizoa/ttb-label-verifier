import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the brains we built in Phase 2
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Label Verifier (Demo)", layout="wide")

# 2. Inject Official Government Header & Test Disclaimer
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0px !important; }
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
       <path d="M32 45 L68 45" stroke="#ffffff" stroke-width="4"/>
    </svg>
    <div style="float: left;">
        <h1 style='margin:0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;'>Alcohol and Tobacco Tax and Trade Bureau</h1>
        <p style='margin:0; font-size: 16px; color: #e1f3f8; margin-top: 5px; font-weight: 400;'>Automated COLA Discrepancy Detection Engine (Technical Demo)</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Layout: Split Screen
col1, col2 = st.columns([1, 1.5]) 

with col1:
    with st.container(border=True):
        st.subheader("1. Government Label Data")
        app_brand = st.text_input("Brand Name")
        app_fanciful = st.text_input("Fanciful Name (Optional)")
        app_type = st.text_input("Class/Type Designation")
        app_abv = st.text_input("Alcohol Content (ABV)")
        app_net = st.text_input("Net Contents")
        app_bottler = st.text_input("Name & Address of Bottler/Importer")
        
        with st.expander("Additional Fields (Wine Specific)"):
            app_appellation = st.text_input("Appellation of Origin")
            app_vintage = st.text_input("Vintage Date")
        
        st.divider() 
        st.subheader("2. Upload Label Artwork")
        uploaded_file = st.file_uploader("Choose a label image", type=["png", "jpg", "jpeg", "svg"])
        
        if uploaded_file:
            if uploaded_file.name.endswith('.svg'):
                svg_string = uploaded_file.getvalue().decode("utf-8")
                st.markdown(svg_string, unsafe_allow_html=True)
            else:
                st.image(uploaded_file, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("3. Automated Verification Audit")
        if uploaded_file and st.button("Run Automated Compliance Check", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    if uploaded_file.name.endswith('.svg'):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
                            f.write(uploaded_file.getvalue())
                            drawing = svg2rlg(f.name)
                            png_io = io.BytesIO()
                            renderPM.drawToFile(drawing, png_io, fmt="PNG")
                            img = Image.open(png_io)
                    else:
                        img = Image.open(uploaded_file)
                    
                    extracted_data = analyze_label_image(img)
                    form_data = {
                        "brand_name": app_brand, "fanciful_name": app_fanciful, 
                        "class_type": app_type, "abv": app_abv, "net_contents": app_net,
                        "bottler_info": app_bottler, "appellation": app_appellation, "vintage": app_vintage
                    }
                    audit_results = verify_compliance({k: v for k, v in form_data.items() if v.strip() != ""}, extracted_data)
                    
                    for element, data in audit_results.items():
                        with st.container(border=True):
                            st.markdown(f"#### {element.replace('_', ' ').title()}")
                            st.write(f"**STATUS:** {data['status']} ({data['confidence']})")
                            c1, c2 = st.columns(2)
                            c1.metric("Expected", data["form"])
                            c2.metric("Extracted", data["label"])
                except Exception as e:
                    st.error(f"Error: {e}")
