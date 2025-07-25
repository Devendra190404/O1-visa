# O-1A Visa Assessment AI System

An AI-powered application designed to automatically evaluate eligibility for the O-1A (Extraordinary Ability) Visa category. The system leverages advanced natural language processing (NLP) techniques, including zero-shot classification and semantic search, to provide an accurate, transparent, and rapid assessment of applicant CVs against official USCIS criteria.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Example Usage](#example-usage)
- [Deployment](#deployment)
- [Support and Issues](#support-and-issues)
- [References](#references)
- [License](#license)

---

## Overview

The O-1A Visa Assessment AI System provides automated eligibility checks for applicants seeking the O-1A visa. By uploading a CV (PDF, DOCX, or TXT), users receive immediate feedback detailing their qualification status, confidence scores for each criterion, and actionable insights.

**Key Benefits:**

- Rapid eligibility assessment without manual intervention.
- Transparent evaluation with confidence scores.
- Scalable and modular multi-agent architecture.
- Easy integration with frontend applications through RESTful APIs.

---

## System Architecture

The system employs a modular multi-agent architecture:

| Component                      | Responsibility                                                     |
|--------------------------------|--------------------------------------------------------------------|
| Document Processing Agent      | Extract raw text from uploaded CV files                            |
| Text Splitting Agent           | Divide text into context-preserving chunks                         |
| Embedding Agent                | Generate semantic embeddings (MPNet-based) and cache using FAISS   |
| Semantic Search Agent          | Retrieve relevant CV sections via semantic similarity              |
| Zero-Shot Classification Agent | Evaluate CV sections against O‑1A criteria using DeBERTa v3 model  |
| Evaluation & Aggregation Agent | Aggregate assessments into a final qualification rating            |

**Workflow:**

```
CV Upload → Document Processing → Text Splitting → Embedding Generation & Caching → Semantic Search → Zero-Shot Classification → Evaluation & Aggregation → API Response
```

---

## Technology Stack

The following technologies are utilized:

| Technology                    | Purpose                                       |
|-------------------------------|-----------------------------------------------|
| Python                        | Core programming language                     |
| FastAPI                       | Backend API server                            |
| Hugging Face Transformers     | NLP models (DeBERTa-v3-large zero-shot model) |
| Sentence Transformers         | Semantic embeddings generation                |
| FAISS                         | Efficient semantic vector search              |
| Gunicorn/Uvicorn              | Production deployment                         |
| Ngrok                         | Local development tunneling                   |

---

## Installation and Setup

Follow these steps to set up the application locally or on your server:

### Step 1: Clone Repository

```bash
git clone https://github.com/DebjyotiRay/Alma.git
cd Alma
```

### Step 2: Set Up Environment

Create a virtual environment (recommended):

```bash
python -m venv env
source env/bin/activate  # Linux/MacOS
.\env\Scripts\activate   # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory and add necessary configurations:

```env
MODEL_NAME=MoritzLaurer/deberta-v3-large-zeroshot-v2.0
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

---

## Running the Application

### Local Development Server

Run the FastAPI server locally:

```bash
uvicorn main:app --reload --port 8000
```

Access the API documentation at:

```
http://localhost:8000/docs
```

### Expose via Ngrok (Optional)

To expose your local server publicly for testing purposes, use Ngrok:

```bash
ngrok http 8000
```

---

## API Documentation

The backend API provides structured endpoints for integration:

| Endpoint                  | Method | Description                                       |
|---------------------------|--------|---------------------------------------------------|
| `/api/analyze`            | POST   | Analyze single CV document                        |
| `/api/batch-analyze`      | POST   | Analyze multiple CV documents at once             |
| `/api/criteria`           | GET    | Retrieve detailed USCIS O‑1A criteria definitions |
| `/api/health`             | GET    | Check system health status                        |

Interactive API documentation is automatically available via FastAPI Swagger UI at:

```
http://localhost:8000/docs
```

---

## Example Usage

### Single CV Analysis Request (cURL):

```bash
curl -X POST "http://localhost:8000/api/analyze" \
-F "cv_file=@/path/to/cv.pdf"
```

### Example JSON Response:

```json
{
  "status": "success",
  "overall_qualification": "Likely Qualified",
  "criteria_evaluations": {
    "Awards": {
      "confidence": 0.88,
      "evaluation": "Strong evidence found."
    },
    "Membership": {
      "confidence": 0.62,
      "evaluation": "Moderate evidence found."
    }
    // Additional criteria...
  },
  "html_report_link": ""
}
```

---

## Support and Issues

For questions or support requests, please open an issue in this repository's GitHub Issues section.

Alternatively, contact maintainers directly via email at `22f3002029@ds.study.iitm.ac.in`.

---

## References

Useful resources for understanding underlying technologies and criteria:

- [USCIS O‑1A Visa Official Information](https://www.uscis.gov/working-in-the-united-states/temporary-workers/o-1-individuals-with-extraordinary-ability-or-achievement)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers/)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [FAISS Vector Search Documentation](https://github.com/facebookresearch/faiss)

