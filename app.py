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
            # --- NEW FIX: Handle SVG Previews safely ---
            if uploaded_file.name.endswith('.svg'):
                # Read the SVG file as text and render it directly using HTML
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
                        # --- NEW SVG CONVERSION LOGIC ---
                        if uploaded_file.name.endswith('.svg'):
                            # Save the uploaded SVG bytes to a temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as f:
                                f.write(uploaded_file.getvalue())
                                tmp_path = f.name
                            
                            # Convert the SVG file into a PNG in memory
                            drawing = svg2rlg(tmp_path)
                            png_io = io.BytesIO()
                            renderPM.drawToFile(drawing, png_io, fmt="PNG")
                            img = Image.open(png_io)
                        else:
                            # Standard image formats proceed normally
                            img = Image.open(uploaded_file)
                        # --------------------------------
                        
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
                        
                        # Filter out empty fields so the UI doesn't clutter with blank comparisons
                        form_data = {k: v for k, v in form_data.items() if v.strip() != ""}
                        
                        # Step 3: Run the compliance engine to compare them
                        audit_results = verify_compliance(form_data, extracted_data)
                        
                        st.write("") 
                        
                        # Step 4: Display the Results beautifully in Material Sub-Cards
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
