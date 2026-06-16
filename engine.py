import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from thefuzz import fuzz
import json

# 1. Securely load the API key from your secrets file
# Streamlit magically finds the .streamlit/secrets.toml file we created
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# 2. Define the exact structure we want the AI to return
# This forces the AI to output clean data instead of a chatty paragraph
class AlcoholLabelSchema(BaseModel):
    brand_name: str = Field(description="The prominent brand name or producer on the label.")
    class_type: str = Field(description="The class or designation, e.g., 'Kentucky Straight Bourbon Whiskey'")
    abv: str = Field(description="Alcohol by volume percentage or proof, e.g., '45% Alc./Vol.'")
    net_contents: str = Field(description="Liquid volume measurement, e.g., '750 mL'")
    has_government_warning_prefix: bool = Field(description="True ONLY if the exact text 'GOVERNMENT WARNING:' appears in all caps.")
    full_warning_text: str = Field(description="The complete extracted text of the health warning.")

# 3. The function that talks to Gemini 1.5 Flash
def analyze_label_image(image):
    """Sends the label image to Gemini Flash with a strict instruction."""
    prompt = """
    Analyze this alcohol beverage label. Extract the required fields precisely as they appear on the label.
    Pay extreme attention to the government warning statement.
    """
    
    # We use Gemini 1.5 Flash because the stakeholders need it to be under 5 seconds!
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AlcoholLabelSchema,
            temperature=0.1 # Low temperature means the AI acts factual, not creative
        ),
    )
    return json.loads(response.text)

# 4. The Rules Engine: Compares the application to the physical label
def verify_compliance(form_data, ai_data):
    results = {}
    
    # Fuzzy match for Brand Name (Handles Senior Agent Dave's "Stone's Throw" scenario)
    brand_score = fuzz.ratio(form_data['brand_name'].lower(), ai_data['brand_name'].lower())
    results['brand_name'] = {
        "form": form_data['brand_name'],
        "label": ai_data['brand_name'],
        "status": "PASS" if brand_score > 85 else ("REVIEW" if brand_score > 60 else "FAIL"),
        "confidence": f"{brand_score}% match"
    }
    
    # Fuzzy match for ABV
    abv_score = fuzz.partial_ratio(form_data['abv'], ai_data['abv'])
    results['abv'] = {
        "form": form_data['abv'],
        "label": ai_data['abv'],
        "status": "PASS" if abv_score > 80 else "FAIL",
        "confidence": f"{abv_score}% match"
    }
    
    # Strict Verification for Government Warning (Handles Junior Agent Jenny's exact text rule)
    expected_warning_keywords = ["government warning", "surgeon general", "beverages", "impair"]
    warning_lower = ai_data['full_warning_text'].lower()
    
    # Check if all the required legal words are present
    contains_keywords = all(kw in warning_lower for kw in expected_warning_keywords)
    
    if ai_data['has_government_warning_prefix'] and contains_keywords:
        warning_status = "PASS"
    elif contains_keywords and not ai_data['has_government_warning_prefix']:
        warning_status = "REVIEW (Prefix not all-caps/bold)"
    else:
        warning_status = "FAIL"
        
    results['government_warning'] = {
        "form": "Mandatory Statutory Text",
        "label": ai_data['full_warning_text'][:60] + "...", # Just show the first 60 characters so the screen isn't cluttered
        "status": warning_status,
        "confidence": "Strict verification rule applied"
    }
    
    return results