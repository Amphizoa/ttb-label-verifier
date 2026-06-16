import streamlit as st
import base64
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import your engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Compliance Portal", layout="wide")

# 2. Styling (USWDS & TTB Precision)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    .stApp { background-color: #f7f7f7; }
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    
    /* Header/Layout Styling */
    .official-banner { background-color: #f0f0f0; padding: 8px 40px; font-size: 13px; border-bottom: 1px solid #aeb0b5; display: flex; align-items: center; }
    .ttb-header { background-color: #003366; color: white; padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; }
    .nav-bar { background-color: #004a80; color: white; padding: 12px 40px; font-weight: 600; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }
    .cbma-banner { background-color: #e7f3ef; border-bottom: 1px solid #aeb0b5; padding: 10px 40px; text-align: center; font-size: 14px; font-weight: bold; }
    .breadcrumbs { background-color: #f0f0f0; padding: 10px 40px; font-size: 13px; font-weight: 700; color: #003366; border-bottom: 1px solid #ddd; }
    .report-fraud-btn { background-color: #2e7d32; color: white !important; padding: 10px 20px; font-weight: 700; border-radius: 4px; text-decoration: none; }
    
    /* Reset borders */
    div[data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background-color: transparent !important; }
    h3 { font-size: 1.5rem; color: #003366; font-weight: 700; margin-bottom: 20px; }
    
    .ttb-footer { background-color: #003366; color: white; padding: 40px 40px; margin-top: 50px; border-top: 5px solid #005ea2; font-size: 13px; }
    .footer-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 40px; max-width: 1200px; margin: 0 auto; }
    .footer-bottom { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 30px auto 0; border-top: 1px solid #005ea2; padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="official-banner">
    <img src="https://images.weserv.nl/?url=https://www.cll.com/assets/htmlimages/Version%20of%20the%20American%20Flag.jpg&w=25" style="margin-right: 10px;">
    An official website of the United States government
</div>
<div class="ttb-header">
    <img src="https://www.ttb.gov/themes/custom/ttb/assets/img/TTB_logo_web.svg" width="300">
    <a href="#" class="report-fraud-btn">Report Fraud: TTB Tips Online</a>
</div>
<div class="nav-bar">
    <div>WHO WE ARE ▾  &nbsp; WHAT WE DO ▾  &nbsp; TTB AUDIENCES ▾  &nbsp; RESOURCES ▾</div>
    <div><i class="fa-solid fa-magnifying-glass" style="margin-right: 8px;"></i>SEARCH</div>
</div>
<div class="cbma-banner">
    <a href="#">CBMA Importer Claims System</a> | <a href="#">CBMA Import Resources</a> | <a href="#">Tax Simplification Pilot Program</a>
</div>
<div class="breadcrumbs">
    HOME > REGULATED COMMODITIES > LABELING > COMPLIANCE CHECK
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. Form
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("1. Government Label Data")
    app_brand = st.text_input("Brand Name")
    app_type = st.text_input("Class/Type Designation")
    app_bottler = st.text_input("Bottler/Importer Address")
    app_fanciful = st.text_input("Fanciful Name (Optional)")

with col2:
    st.subheader("2. Supplementary Data")
    app_abv = st.text_input("Alcohol Content (ABV)")
    app_net = st.text_input("Net Contents")
    app_vintage = st.text_input("Vintage Date (Optional)")
    app_appellation = st.text_input("Appellation of Origin")

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("3. Upload Label Artwork")
uploaded_file = st.file_uploader("Choose a label file", type=["png", "jpg", "jpeg", "svg"], label_visibility="collapsed")

# 5. Audit Execution (Logic Restored)
if uploaded_file and st.button("Run Automated Compliance Check", type="primary"):
    with st.spinner("Executing official TTB regulatory audit..."):
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
            
            st.markdown("### Audit Findings")
            for element, data in audit_results.items():
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
    <div style="text-align: center; margin-bottom: 40px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/4d/US-AlcoholAndTobaccoTaxAndTradeBureau-Seal.svg" width="80">
    </div>
    <div class="footer-grid">
        <div><strong>Filing & Payments</strong><br>Permits Online<br>COLAs Online<br>Tax Returns</div>
        <div><strong>About TTB</strong><br>Contact Us<br>Offices<br>Careers</div>
        <div><strong>Additional Information</strong><br>Open Government<br>Plain Language</div>
        <div><strong>Additional Resources</strong><br>FOIA<br>Report Fraud</div>
        <div><strong>Other Govt Sites</strong><br>Dept. of the Treasury<br>USA.gov</div>
        <div><strong>Language Links</strong><br>En Español<br>Français<br>漢語</div>
    </div>
    <div class="footer-bottom">
        <span>Accessibility  |  Privacy Policy</span>
        <div style="font-size: 18px;">
            <i class="fas fa-file-alt" style="margin-left: 15px;"></i> 
            <i class="fas fa-rss" style="margin-left: 15px;"></i> 
            <i class="fas fa-envelope" style="margin-left: 15px;"></i> 
            <i class="fas fa-calendar-alt" style="margin-left: 15px;"></i> 
            <i class="fas fa-user-gear" style="margin-left: 15px;"></i>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
