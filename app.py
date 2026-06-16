import streamlit as st
from PIL import Image
import io
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Import the logic engine
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="TTB Label Verifier (Demo)", layout="wide")

# 2. Inject Official Federal Reserve-Style Header
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@700&family=Public+Sans:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Public Sans', sans-serif !important; }
    h1 { font-family: 'Merriweather', serif !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 0px !important; border: 1px solid #dcdcdc; }
</style>

<div style='background-color: #003366; color: #ffffff; padding: 20px; border-bottom: 3px solid #cc0000; display: flex; align-items: center;'>
    <img src="https://www.federalreserve.gov/assets/homepage/images/logo-fed-reserve.png" 
         alt="Federal Reserve Logo" 
         style="width: 200px; margin-right: 30px; filter: brightness(0) invert(1);">
    <div>
        <h1 style='margin:0; color: #ffffff; font-size: 24px;'>Board of Governors of the Federal Reserve System</h1>
        <p style='margin:0; font-size: 14px; color: #d1d1d1; margin-top: 5px;'>Compliance & Regulatory Discrepancy Detection Portal</p>
    </div>
</div>

<div style='background-color: #fff8e1; color: #856404; padding: 10px 20px; font-size: 13px; text-align: center; border-bottom: 1px solid #ffeeba;'>
    <strong>TEST CASE ONLY:</strong> Built for technical interview assessment. Not an official regulatory interface.
</div>
""", unsafe_allow_html=True)

# 3. Layout: Input & Audit Sections
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
                    # Robust SVG-to-PNG conversion logic
                    if uploaded_file.name.endswith('.svg'):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
                            f.write(uploaded_file.getvalue())
                            drawing = svg2rlg(f.name)
                            if drawing is None:
                                raise ValueError("Malformed SVG file.")
                            png_io = io.BytesIO()
                            renderPM.drawToFile(drawing, png_io, fmt="PNG")
                            img = Image.open(png_io)
                    else:
                        img = Image.open(uploaded_file)
                    
                    # AI Extraction
                    extracted_data = analyze_label_image(img)
                    
                    # Compliance Verification
                    form_data = {
                        "brand_name": app_brand, "fanciful_name": app_fanciful, 
                        "class_type": app_type, "abv": app_abv, "net_contents": app_net,
                        "bottler_info": app_bottler, "appellation": app_appellation, "vintage": app_vintage
                    }
                    audit_results = verify_compliance({k: v for k, v in form_data.items() if v.strip() != ""}, extracted_data)
                    
                    # Display Results
                    for element, data in audit_results.items():
                        with st.container(border=True):
                            st.markdown(f"#### {element.replace('_', ' ').title()}")
                            st.write(f"**STATUS:** {data['status']} ({data['confidence']})")
                            c1, c2 = st.columns(2)
                            c1.metric("Expected", data["form"])
                            c2.metric("Extracted", data["label"])
                            
                except Exception as e:
                    st.error(f"Error: {e}")
