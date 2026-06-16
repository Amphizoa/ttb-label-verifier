import streamlit as st
from PIL import Image
import io
import tempfile
import base64
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import your engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Compliance Portal", layout="wide")

# 2. Flag as Base64 (Reliable Rendering)
flag_b64 = "iVBORw0KGgoAAAANSUhEUgAAAGQAAABACAYAAACy4+8LAAAACXBIWXMAAAsTAAALEwEAmpwYAAAKTWlDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNfSFNhHMb/nXPuvrV0U1o6W0pISx8p0vLhN1+aQZt0lB4a6mXk3H2ZfQd31713v9f09Pz6P4G+g09+9P55P8C8nS6+7+15HhM5j4r/n+f9+XwHAPw12QIAaC8EIMgYhBw0oE6D64pBv/D4T/h32H+DqgqW2E7r43X3x5x6O6B55D6f5Z6Qv36+u599oKAB0HwGgQ1sIAeGvOBAwF6JADxY0H2QpP1k7hO9pW0s5Z68vJ9wLg6R6Wb2Q+oH18N5e2l/uD7QPAx4K9rWjNf1c6o1Y4u2B4P0uW0Z1i00G2y18j3QW4+1nLhN9Z5Fq5P6/gZ+yBqXyM1/5wF9C/n38s3yG/uD+f5sV88G04Z5JcWnC/JvJ8eT14X+U9Fm0G0z7Z+PzM1YVz9Jm96bF91G3e+v+u9oYp638J/pB0O1jO8t5G/6/gW0G99i898r446gH5O9B0vV0O5Xz4g98s/8i8985y8h91Dqg5DqgJ13+P8v4034b7f4A=="

# 3. TTB-Specific Branding & Layout CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap');
    .stApp { background-color: #f7f7f7; }
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    
    .official-banner { background-color: #f0f0f0; color: #1b1b1b; padding: 10px 20px; font-size: 13px; border-bottom: 1px solid #aeb0b5; display: flex; align-items: center; }
    .ttb-header { background-color: #003366; color: white; padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; }
    .nav-bar { background-color: #004a80; color: white; padding: 12px 40px; font-weight: bold; font-size: 14px; display: flex; justify-content: space-between; }
    .ttb-footer { background-color: #003366; color: white; padding: 40px 20px; margin-top: 50px; border-top: 5px solid #005ea2; font-size: 13px; text-align: center; }
    
    .report-fraud-btn { background-color: #2e7d32; color: white !important; padding: 12px 24px; font-weight: bold; border-radius: 4px; text-decoration: none; display: inline-block; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0px !important; border: 1px solid #aeb0b5 !important; background-color: #ffffff; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# 4. Header Section
st.markdown("""
<div class="official-banner">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/25px-Flag_of_the_United_States.svg.png" style="margin-right: 10px;">
    An official website of the United States government
</div>
<div class="ttb-header">
    <img src="https://www.ttb.gov/themes/custom/ttb/assets/img/TTB_logo_web.svg" width="300">
    <a href="#" class="report-fraud-btn">Report Fraud: TTB Tips Online</a>
</div>
<div class="nav-bar">
    <div>WHO WE ARE ▾  |  WHAT WE DO ▾  |  TTB AUDIENCES ▾  |  RESOURCES ▾</div>
    <div>🔍 SEARCH</div>
</div>
""", unsafe_allow_html=True)

# 5. Main Application Form
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

# 6. Audit Logic
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

# 7. Official Footer
st.markdown("""
<div class="ttb-footer">
    <img src="https://upload.wikimedia.org/wikipedia/commons/4/4d/US-AlcoholAndTobaccoTaxAndTradeBureau-Seal.svg" width="80" style="margin-bottom: 20px;">
    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 20px; text-align: left; max-width: 1100px; margin: 0 auto; font-size: 13px;">
        <div><strong>Filing & Payments</strong><br>Permits Online<br>COLAs Online<br>Tax Returns<br>Permit Applications<br>Submit a Claim Online</div>
        <div><strong>About TTB</strong><br>Contact Us<br>Offices<br>Careers<br>Regulations</div>
        <div><strong>Additional Information</strong><br>Open Government<br>Plain Language<br>Information Quality<br>Forms<br>Labeling</div>
        <div><strong>Additional Resources</strong><br>FOIA<br>Whistleblower Protection<br>Report Fraud</div>
        <div><strong>Other Govt Sites</strong><br>Dept. of the Treasury<br>USA.gov<br>Data.gov<br>Internal Revenue Service<br>Office of Special Counsel</div>
        <div><strong>Language Links</strong><br>En Español<br>Français<br>漢語</div>
    </div>
    <hr style="border: 0.5px solid #005ea2; margin: 30px auto; max-width: 1000px;">
    <div style="display: flex; justify-content: center; gap: 20px; align-items: center;">
        <span>Accessibility  |  Privacy Policy</span>
        <span style="font-size: 20px;">📄 ⋈ ✉️ 📅 ⚙️</span>
    </div>
</div>
""", unsafe_allow_html=True)
