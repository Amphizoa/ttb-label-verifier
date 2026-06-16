import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the logic engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Label Compliance Engine", layout="wide")

# 2. Inject Official TTB / USWDS Header & Banner
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;700&display=swap');
    
    .stApp { background-color: #f0f0f0; } /* Federal gray background */
    
    /* Official USWDS Typography */
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    
    /* TTB Style Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        border-radius: 0px !important; 
        border: 1px solid #aeb0b5 !important; 
        background-color: #ffffff;
        padding: 20px;
    }
</style>

<div style='background-color: #f0f0f0; color: #1b1b1b; padding: 10px 20px; font-size: 13px; border-bottom: 1px solid #aeb0b5;'>
    <img src="https://www.usa.gov/sites/usa/themes/uswds/dist/img/favicon-57.png" width="20" style="margin-right: 5px;">
    An official website of the <strong>United States government</strong>
</div>

<div style='background-color: #005ea2; color: #ffffff; padding: 30px 20px; border-bottom: 4px solid #1a1a1a;'>
    <h1 style='margin:0; font-size: 32px; font-weight: 700;'>Alcohol and Tobacco Tax and Trade Bureau</h1>
    <p style='margin:0; font-size: 18px; margin-top: 5px; color: #d1d1d1;'>COLA Compliance Discrepancy Detection Engine</p>
</div>

<div style='background-color: #fac22b; color: #1a1a1a; padding: 10px 20px; font-size: 14px; font-weight: bold; text-align: center; border-bottom: 2px solid #1a1a1a;'>
    DEMONSTRATION PROTOTYPE: Built for technical assessment. Not an official TTB tool.
</div>
""", unsafe_allow_html=True)

# 3. Layout: Two-Column Form
col1, col2 = st.columns([1, 1]) 

with col1:
    with st.container(border=True):
        st.markdown("### 1. Government Label Data")
        st.info("Enter the application data exactly as submitted in your COLA application.")
        app_brand = st.text_input("Brand Name")
        app_type = st.text_input("Class/Type Designation")
        app_bottler = st.text_input("Bottler/Importer Address")
        app_fanciful = st.text_input("Fanciful Name (Optional)")

with col2:
    with st.container(border=True):
        st.markdown("### 2. Supplementary Data")
        st.info("Ensure all wine-specific details match the submitted documentation.")
        app_abv = st.text_input("Alcohol Content (ABV)")
        app_net = st.text_input("Net Contents")
        app_vintage = st.text_input("Vintage Date (Optional)")
        app_appellation = st.text_input("Appellation of Origin")

st.markdown("---")
st.subheader("3. Upload Label Artwork")
st.info("Upload the primary label artwork for the automated audit.")
uploaded_file = st.file_uploader("Choose a label file", type=["png", "jpg", "jpeg", "svg"])

if uploaded_file:
    if uploaded_file.name.endswith('.svg'):
        svg_string = uploaded_file.getvalue().decode("utf-8")
        st.markdown(svg_string, unsafe_allow_html=True)
    else:
        st.image(uploaded_file, use_container_width=True)

# 4. Audit Execution
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
            form_data = {
                "brand_name": app_brand, "fanciful_name": app_fanciful, 
                "class_type": app_type, "abv": app_abv, "net_contents": app_net,
                "bottler_info": app_bottler, "appellation": app_appellation, "vintage": app_vintage
            }
            audit_results = verify_compliance({k: v for k, v in form_data.items() if v.strip() != ""}, extracted_data)
            
            st.markdown("---")
            st.markdown("### Audit Findings")
            for element, data in audit_results.items():
                with st.container(border=True):
                    st.markdown(f"#### {element.replace('_', ' ').title()}")
                    st.write(f"**STATUS:** {data['status']}")
                    c1, c2 = st.columns(2)
                    c1.metric("Expected", data["form"])
                    c2.metric("Extracted", data["label"])
        except Exception as e:
            st.error(f"Audit Error: {e}")
