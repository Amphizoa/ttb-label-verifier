import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import your engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Compliance Portal", layout="wide")

# 2. TTB-Specific Branding & Layout CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap');
    .stApp { background-color: #f7f7f7; }
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    
    .official-banner { background-color: #f0f0f0; color: #1b1b1b; padding: 10px 20px; font-size: 13px; border-bottom: 1px solid #aeb0b5; display: flex; align-items: center; }
    .ttb-header { background-color: #003366; color: white; padding: 20px; display: flex; align-items: center; }
    .nav-bar { background-color: #004a80; color: white; padding: 12px 20px; font-weight: bold; font-size: 14px; }
    .ttb-footer { background-color: #003366; color: white; padding: 40px 20px; margin-top: 50px; border-top: 5px solid #005ea2; font-size: 13px; text-align: center; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0px !important; border: 1px solid #aeb0b5 !important; background-color: #ffffff; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. Header Section (Using provided custom flag)
st.markdown("""
<div class="official-banner">
    <img src="https://i.imgur.com/kS9Z0aY.png" width="25" style="margin-right: 10px;">
    An official website of the United States government
</div>
<div class="ttb-header">
    <img src="https://www.ttb.gov/themes/custom/ttb/assets/img/TTB_logo_web.svg" width="300">
</div>
<div class="nav-bar">
    WHO WE ARE ▾  |  WHAT WE DO ▾  |  TTB AUDIENCES ▾  |  RESOURCES ▾
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. Main Application Form
col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.markdown("### 1. Government Label Data")
        app_brand = st.text_input("Brand Name")
        app_type = st.text_input("Class/Type Designation")
        app_bottler = st.text_input("Bottler/Importer Address")
        app_fanciful = st.text_input("Fanciful Name (Optional)")

with col2:
    with st.container(border=True):
        st.markdown("### 2. Supplementary Data")
        app_abv = st.text_input("Alcohol Content (ABV)")
        app_net = st.text_input("Net Contents")
        app_vintage = st.text_input("Vintage Date (Optional)")
        app_appellation = st.text_input("Appellation of Origin")

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("3. Upload Label Artwork")
uploaded_file = st.file_uploader("Choose a label file", type=["png", "jpg", "jpeg", "svg"])

# 5. Audit Logic
if uploaded_file and st.button("Run Automated Compliance Check", type="primary"):
    with st.spinner("Executing TTB regulatory audit..."):
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
            form_data = {"brand_name": app_brand, "fanciful_name": app_fanciful, "class_type": app_type, "abv": app_abv, "net_contents": app_net, "bottler_info": app_bottler, "appellation": app_appellation, "vintage": app_vintage}
            audit_results = verify_compliance({k: v for k, v in form_data.items() if v.strip() != ""}, extracted_data)
            
            for element, data in audit_results.items():
                with st.container(border=True):
                    st.markdown(f"#### {element.replace('_', ' ').title()}")
                    st.write(f"**STATUS:** {data['status']}")
                    c1, c2 = st.columns(2)
                    c1.metric("Expected", data["form"])
                    c2.metric("Extracted", data["label"])
        except Exception as e:
            st.error(f"Audit Error: {e}")

# 6. Official Footer
st.markdown("""
<div class="ttb-footer">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/US-AlcoholAndTobaccoTaxAndTradeBureau-Seal.svg/100px-US-AlcoholAndTobaccoTaxAndTradeBureau-Seal.svg.png" width="80" style="margin-bottom: 20px;">
    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 40px; text-align: left; max-width: 1000px; margin: 0 auto;">
        <div><strong>Filing & Payments</strong><br>Permits Online<br>COLAs Online<br>
