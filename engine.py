import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from thefuzz import fuzz

# 1. Define the exact strict schema we want the AI to return
class LabelData(BaseModel):
    brand_name: str = Field(description="The primary brand name or producer of the alcohol.")
    fanciful_name: str = Field(description="Any secondary fanciful or creative name.", default="Not Found")
    class_type: str = Field(description="The class and type designation (e.g., Bourbon, Tequila, IPA, Cabernet Sauvignon).")
    abv: str = Field(description="Alcohol by volume (e.g., 45% Alc./Vol., 7.2%).")
    net_contents: str = Field(description="The volume of the liquid (e.g., 750 mL, 1 Pint).")
    bottler_info: str = Field(description="Name and address of bottler, importer, or brewer.", default="Not Found")
    appellation: str = Field(description="Appellation of origin (mostly for wine, e.g., Napa Valley).", default="Not Found")
    vintage: str = Field(description="Vintage year (e.g., 2019).", default="Not Found")

def analyze_label_image(img):
    """Sends the image to Gemini 2.5 Flash and forces a structured JSON response."""
    client = genai.Client() # Automatically picks up GEMINI_API_KEY from environment/secrets
    
    prompt = "Analyze this alcohol label and extract the following compliance fields exactly as they appear."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LabelData,
        ),
    )
    
    # Convert the AI's JSON string back into a standard Python dictionary
    return json.loads(response.text)

def verify_compliance(form_data, extracted_data):
    """Compares the expected form data against the AI-extracted data using fuzzy matching."""
    results = {}
    
    for key, expected_value in form_data.items():
        # --- THE FIX IS HERE ---
        # Using .get() prevents the app from crashing if the AI completely missed a key
        extracted_value = extracted_data.get(key, "Not Found")
        
        # Calculate how closely the two strings match (0 to 100)
        score = fuzz.token_sort_ratio(str(expected_value).lower(), str(extracted_value).lower())
        
        # Determine pass/fail based on the fuzzy match score
        if score >= 90:
            status = "✅ PASS"
        elif score >= 60:
            status = "⚠️ REVIEW"
        else:
            status = "❌ FAIL"
            
        results[key] = {
            "status": status,
            "confidence": f"{score}% Match",
            "form": expected_value,
            "label": extracted_value
        }
        
    return results
