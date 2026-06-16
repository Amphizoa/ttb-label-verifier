# Alcohol Label Verifier (TTB Compliance Engine)

**Live Demo:** [[Insert Your Streamlit App URL Here]](https://ttb-label-verifier-6kmsnf96euzsrakkxksvag.streamlit.app/)

## Overview
The Alcohol Label Verifier is a prototype automated compliance engine designed to detect discrepancies between official government application data (COLA) and actual physical bottle label artwork. 

Built with a focus on speed and accuracy, this tool leverages multimodal large language models to instantly extract text, classify parameters, and cross-reference government application data against uploaded packaging images.

## Features
* **Automated Discrepancy Detection:** Instantly cross-references form inputs (Brand, ABV, Net Contents, Class) against visual label elements.
* **High-Speed Processing:** Optimized to return audit results in under 5 seconds to meet strict operational workflow requirements.
* **Modern Interface:** A clean, Material-inspired UI built with Streamlit for intuitive application data entry and image uploading.
* **Confidence Scoring:** Outputs pass/fail/review statuses alongside the expected versus extracted data for rapid human-in-the-loop verification.

## Technology Stack
* **Frontend/Deployment:** Streamlit & Streamlit Community Cloud
* **AI/Computer Vision:** Google Gemini 2.5 Flash API (`google-genai`)
* **Image Processing:** Pillow (PIL)
* **Logic/Fuzzy Matching:** `thefuzz`

---

## Architectural Decisions & Engineering Trade-offs

During the development of this prototype, several key architectural decisions were made to balance accuracy, latency, and reliability:

### 1. Model Selection & Quota Management
While frontier reasoning models (like Gemini 3.1 Pro Preview) offer enhanced zero-shot accuracy, I explicitly architected this prototype utilizing **Gemini 2.5 Flash**. 
* **Latency Requirement:** The Flash architecture guarantees we meet the strict < 5-second latency requirement for end-users, whereas heavier models frequently exceed this threshold.
* **Rate Limiting:** Using Flash bypasses the strict rate-limiting (HTTP 429 Resource Exhausted) associated with free-tier Pro models, ensuring high availability during the review process.

### 2. Handling API Limits & Resiliency
As a cloud-dependent prototype using a free-tier LLM API, occasional `503 Service Unavailable` errors may occur during unexpected traffic spikes on Google's servers. 
* *Future Production Enhancement:* In a production deployment, I would implement an **Exponential Backoff** retry mechanism (utilizing a library such as `tenacity`) around the API call block. This would automatically re-attempt the API call in the background, masking transient network or server errors from the compliance agent interacting with the UI.

---

## Running the Application Locally

### Prerequisites
* Python 3.9+
* A Google Gemini API Key

### Installation & Execution

Run the following commands in your terminal to clone the repository, set up your environment, inject your API key, and launch the application:

```bash
# 1. Clone the repository and navigate into it
git clone [https://github.com/Amphizoa/ttb-label-verifier.git](https://github.com/Amphizoa/ttb-label-verifier.git)
cd ttb-label-verifier

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Note: On Windows, use `venv\Scripts\activate`

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API Key
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your_actual_api_key_here"' > .streamlit/secrets.toml

# 5. Run the application
streamlit run app.py
