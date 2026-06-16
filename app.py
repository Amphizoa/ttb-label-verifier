import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the logic engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="Compliance Portal (Demo)", layout="wide")

# 2. Inject Official Federal-Style CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Georgia&family=Public+Sans:wght@400;600&display=swap');
    .stApp { background-color: #f7f7f7; }
    h1, h2, h3 { font-family: 'Georgia', serif !important; color: #003366 !important; }
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border-radius: 0px !important; 
        border: 1px solid #c0c0c0 !important; 
        background-color: #ffffff;
    }
</style>

<div style='background-color: #003366; color: #ffffff; padding: 20px; border-bottom: 3px solid #cc0000; display: flex; align-items: center;'>
    <div style='font-family: Georgia, serif; font-size: 30px; font-weight: bold; border: 2px solid white; padding: 5px 15px; margin-right: 25px;'>FRB</div>
    <div>
        <h1 style='margin:0; color: #ffffff !important; font-size: 24px;'>Board of Governors of the Federal Reserve System</h1>
        <p style='margin:0; font-size: 14px; color: #d1d1d1; margin-top: 5px;'>Compliance & Regulatory Discrepancy Detection Portal</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Layout: Two-Column Federal Form Grid
col1, col2 = st.columns([1, 1]) 

with col1:
    with st.container(border=True):
        st.markdown("### 1. Primary Identifiers")
        st.info("Enter the information exactly as it appears on your official application form.")
        app_brand = st.text_input("Brand Name")
        app_type = st.text_input("Class/Type Designation")
        app_bottler = st.text_input("Bottler/Importer Address")
        app_fanciful = st.text_input("Fanciful Name (Optional)")

with col2:
    with st.container(border=True):
        st.markdown("### 2. Supplementary Data")
        st.info("Include all auxiliary label details required for specific commodity compliance.")
        app_abv = st.text_input("Alcohol Content (ABV)")
        app_net = st.text_input("Net Contents")
        app_vintage = st.text_input("Vintage Date (Optional)")
        app_appellation = st.text_input("Appellation of Origin")

st.markdown("---")
st.subheader("3. Upload Label Artwork")
st.info("Upload the high-resolution label file (PNG, JPG, or SVG) that corresponds to the data entered above.")
uploaded_file = st.file_uploader("Choose a label image", type=["png", "jpg", "jpeg", "svg"])

if uploaded_file:
    if uploaded_file.name.endswith('.svg'):
        svg_string = uploaded_file.getvalue().decode("utf-8")
        st.markdown(svg_string, unsafe_allow_html=True)
    else:
        st.image(uploaded_file, use_container_width=True)

# 4. Audit Execution
if uploaded_file and st.button("Run Automated Compliance Check", type="primary"):
    with st.spinner("Processing official compliance audit..."):
        try:
            # SVG Parsing
            if uploaded_file.name.endswith('.svg'):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
                    f.write(uploaded_file.getvalue())
                drawing = svg2rlg(f.name)
                png_io = io.BytesIO()
                renderPM.drawToFile(drawing, png_io, fmt="PNG")
                img = Image.open(png_io)
            else:
                img = Image.open(uploaded_file)
            
            # AI Logic
            extracted_data = analyze_label_image(img)
            form_data = {
                "brand_name": app_brand, "fanciful_name": app_fanciful, 
                "class_type": app_type, "abv": app_abv, "net_contents": app_net,
                "bottler_info": app_bottler, "appellation": app_appellation, "vintage": app_vintage
            }
            audit_results = verify_compliance({k: v for k, v in form_data.items() if v.strip() != ""}, extracted_data)
            
            # Result Display
            st.markdown("---")
            st.markdown("### Audit Findings")
            st.info("Verified against 27 CFR Part 4 regulatory requirements.")
            for element, data in audit_results.items():
                with st.container(border=True):
                    st.markdown(f"#### {element.replace('_', ' ').title()}")
                    st.write(f"**STATUS:** {data['status']}")
                    c1, c2 = st.columns(2)
                    c1.metric("Expected", data["form"])
                    c2.metric("Extracted", data["label"])
        except Exception as e:
            st.error(f"Audit Error: {e}")
