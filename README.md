# Alcohol Label Verifier (TTB Compliance Engine)

**Live Demo:** https://ttb-label-verifier-6kmsnf96euzsrakkxksvag.streamlit.app/]

## 1. Project Overview
The Alcohol Label Verifier is an automated compliance engine designed to modernize the TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA (Certification/Exemption of Label/Bottle Approval) review process. 

By leveraging multimodal Large Language Models (LLMs) and fuzzy string matching, this prototype detects discrepancies between official government application data and actual physical bottle label artwork. It reduces manual review times, mitigates human error, and accelerates time-to-market for alcohol producers by providing instantaneous, confidence-scored audits of mandatory labeling requirements (e.g., ABV, Net Contents, Bottler Information, and Surgeon General Warnings).

## 2. Core Architecture & Data Flow

The application executes a four-step pipeline to evaluate compliance:

1. **Data Ingestion:** The user inputs baseline COLA application data via a structured Streamlit form and uploads high-resolution label artwork (PNG, JPG, or SVG).
2. **Vector Graphic Pre-Processing:** If vector artwork (.svg) is uploaded, a pure-Python conversion pipeline intercepts the file. Utilizing a system-level Cairo backend, the vector is safely rasterized into an in-memory PNG to prevent text degradation and bypass standard PIL compatibility issues.
3. **Multimodal Extraction:** The rasterized image and a strict extraction prompt are sent to the Google Gemini API. The AI engine utilizes `pydantic` schemas to guarantee the return payload is formatted as strict, parseable JSON containing the exact fields required by the compliance engine.
4. **Fuzzy Logic Evaluation:** The `verify_compliance` engine cross-references the user's expected data against the AI's extracted data. It utilizes Levenshtein distance to calculate a similarity score, allowing the system to gracefully handle minor OCR errors or formatting differences.

---

## 3. Codebase Walkthrough

To ensure maintainability, the application logic is decoupled into two primary files: the frontend interface (`app.py`) and the artificial intelligence backend (`engine.py`).

### Frontend Implementation (`app.py`)
Built with Streamlit, the frontend operates on a reactive, two-column layout. 
* **State Management:** The application relies on Streamlit's native top-down execution flow. Form inputs are bound to variables that are conditionally bundled into a dictionary (`form_data`) only when the primary execution button is triggered.
* **Empty Field Filtering:** Before sending the expected data to the engine, dictionary comprehension (`{k: v for k, v in form_data.items() if v.strip() != ""}`) strips out any optional fields the user left blank. This prevents the UI from cluttering the results screen with blank comparisons.
* **Conditional UI Rendering:** To bypass `Pillow`'s inability to render SVG XML natively, the app inspects the `uploaded_file.name`. If the file is an SVG, the UI decodes the byte stream into utf-8 and injects it directly into the DOM using `st.markdown(unsafe_allow_html=True)`.

### Intelligence Backend (`engine.py`)
This file orchestrates the Google Gemini LLM and the scoring algorithm.
* **Strict JSON Enforcement:** The `LabelData` class inherits from Pydantic's `BaseModel`. This is passed directly into the Gemini API's `response_schema` parameter. This forces the LLM to abandon standard prose generation and return an exact, predictable JSON object, preventing parsing errors.
* **Levenshtein Distance Scoring:** The `verify_compliance` function iterates over the expected keys and uses `thefuzz.token_sort_ratio()`. This specific algorithm tokenizes strings, sorts them alphabetically, and compares them. This ensures that "Old Tom Distillery, Frankfort KY" and "Frankfort KY, Old Tom Distillery" evaluate to a nearly 100% match, whereas strict string comparison would fail them entirely.

---

## 4. Technology Stack & Dependencies

* **Frontend Framework:** Streamlit (Python)
* **AI/Reasoning Engine:** Google Gemini 2.5 Flash (`google-genai`)
* **Structured Data:** `pydantic`
* **Logic/Fuzzy Matching:** `thefuzz`
* **Image Processing:** `Pillow` (PIL)
* **SVG Processing:** `svglib`, `reportlab`, `rlPyCairo`

---

## 5. Engineering Trade-offs & Design Decisions

### Confidence Scoring vs. Binary Pass/Fail
Instead of a strict binary evaluation, the system implements a tiered confidence scoring mechanism:
* **PASS (> 90% Match):** Safe for automated approval.
* **REVIEW (60% - 89% Match):** Flags minor discrepancies (e.g., missing commas, slight abbreviation differences) for human-in-the-loop verification.
* **FAIL (< 60% Match):** High probability of a compliance violation or missing mandatory field.

### API Quota Management & Latency
While frontier reasoning models offer enhanced zero-shot accuracy, I explicitly architected this prototype utilizing **Gemini 2.5 Flash**. The Flash architecture guarantees we meet the strict < 5-second latency requirement for end-users and bypasses aggressive rate-limiting associated with free-tier Pro models.

### Graceful Failure Handling
The AI extraction engine utilizes safe `.get()` dictionary methods with explicit "Not Found" fallbacks (`extracted_data.get(key, "Not Found")`). This prevents application crashes (KeyErrors) if the LLM completely fails to identify a required field on highly complex or visually noisy label artwork.

---

## 6. Local Setup & Installation Guide

### Prerequisites
* Python 3.9+
* A Google Gemini API Key
* **System Graphics Drivers:** If testing SVG files locally, you must have Cairo installed on your machine (e.g., `brew install cairo` for macOS, `sudo apt-get install libcairo2-dev` for Ubuntu).

### Execution Steps
Run the following commands in your terminal to initialize the project:

```bash
# 1. Clone the repository
git clone [https://github.com/Amphizoa/ttb-label-verifier.git](https://github.com/Amphizoa/ttb-label-verifier.git)
cd ttb-label-verifier

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure your API Key securely
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your_actual_api_key_here"' > .streamlit/secrets.toml

# 5. Launch the local server
streamlit run app.py
