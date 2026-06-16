import streamlit as st
from PIL import Image

# Import the brains we built in Phase 2
from engine import analyze_label_image, verify_compliance

# 1. Page Configuration
st.set_page_config(page_title="Alcohol Label Verifier", layout="wide")

# Main Header - Clean and simple
st.title("Alcohol Label Verifier")

# 2. Layout: Split Screen with Material-style "Cards"
# Adjusted the ratio slightly so the results card has more horizontal space
col1, col2 = st.columns([1, 1.5]) 

with col1:
    # MATERIAL CARD 1: Input Data
    with st.container(border=True):
        st.subheader("1. Government Record Input")
        st.caption("Simulated government record data.")
        
       # Form Data inputs (Empty by default so you can enter fresh data)
        app_brand = st.text_input("Brand Name", "")
        app_type = st.text_input("Class/Type Designation", "")
        app_abv = st.text_input("Alcohol Content (ABV)", "")
        app_net = st.text_input("Net Contents", "")
        
        st.divider() # Clean material-style subtle line separator
        
        st.subheader("2. Upload Label Artwork")
        uploaded_file = st.file_uploader("Choose a label image", type=["png", "jpg", "jpeg"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Label Artwork Ready for Review", use_container_width=True)

with col2:
    # MATERIAL CARD 2: Audit Results Engine
    with st.container(border=True):
        st.subheader("3. Automated Verification Audit")
        st.caption("AI-powered discrepancy analysis.")
        
        if uploaded_file:
            # A massive, obvious primary button (No hunting for buttons!)
            if st.button(" Run Automated Compliance Check", type="primary", use_container_width=True):
                
                with st.spinner("Analyzing image features and running logic rules... (Expected: < 5s)"):
                    try:
                        # Convert the uploaded file into an Image object for Gemini
                        img = Image.open(uploaded_file)
                        
                        # Step 1: Have the AI read the label
                        extracted_data = analyze_label_image(img)
                        
                        # Step 2: Bundle the form data from the left column
                        form_data = {
                            "brand_name": app_brand,
                            "class_type": app_type,
                            "abv": app_abv,
                            "net_contents": app_net
                        }
                        
                        # Step 3: Run the compliance engine to compare them
                        audit_results = verify_compliance(form_data, extracted_data)
                        
                        st.write("") # Vertical spacing before results
                        
                        # Step 4: Display the Results beautifully in Material Sub-Cards
                        for element, data in audit_results.items():
                            
                            # Wrapping each result in its own elevated card for ultimate readability
                            with st.container(border=True):
                                st.markdown(f"#### {element.replace('_', ' ').title()}")
                                
                                # Clean Color-Coded Badges based on status
                                if "PASS" in data["status"]:
                                    st.success(f"**STATUS: {data['status']}** ({data['confidence']})")
                                elif "REVIEW" in data["status"]:
                                    st.warning(f"**STATUS: {data['status']}** ({data['confidence']})")
                                else:
                                    st.error(f"**STATUS: {data['status']}** ({data['confidence']})")
                                    
                                # Put the expected vs extracted data side-by-side
                                metric_c1, metric_c2 = st.columns(2)
                                metric_c1.metric("Expected (Form Value)", data["form"])
                                metric_c2.metric("Extracted (From Label)", data["label"])
                            
                    except Exception as e:
                        st.error(f"An error occurred during verification processing: {e}")
                        st.info("Check your terminal to ensure your API key is correct and you have internet access.")
        else:
            st.info(" Please input label data manually from the database and upload a label image on the left to run the compliance engine.")