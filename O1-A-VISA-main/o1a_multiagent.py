#!/usr/bin/env python
"""
O-1A visa assessment multi-agent system using HuggingFace models.
This implementation uses DeBERTa-v3 models for zero-shot classification
instead of requiring OpenAI API keys.
"""

import os
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import tempfile
import time

# Document processing
import fitz  # PyMuPDF for PDF processing
import docx2txt  # For DOCX processing

# Hugging Face transformers
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document as LangchainDocument

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("o1a_multiagent")

# Define enums and structured data classes for O-1A assessment
class QualificationRating(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CriterionAssessment:
    def __init__(self, matches: List[str] = None, confidence: float = 0.0, evaluation: str = ""):
        self.matches = matches or []
        self.confidence = confidence
        self.evaluation = evaluation
    
    def to_dict(self):
        return {
            "matches": self.matches,
            "confidence": self.confidence,
            "evaluation": self.evaluation
        }

class O1AAssessment:
    def __init__(self, matches_by_criterion: Dict[str, List[str]] = None, 
                qualification_rating: QualificationRating = QualificationRating.LOW, 
                rating_explanation: str = "", 
                detailed_assessment: Dict[str, CriterionAssessment] = None):
        self.matches_by_criterion = matches_by_criterion or {}
        self.qualification_rating = qualification_rating
        self.rating_explanation = rating_explanation
        self.detailed_assessment = detailed_assessment or {}
    
    def to_dict(self):
        return {
            "matches_by_criterion": self.matches_by_criterion,
            "qualification_rating": self.qualification_rating,
            "rating_explanation": self.rating_explanation,
            "detailed_assessment": {k: v.to_dict() for k, v in self.detailed_assessment.items()}
        }

# O-1A criteria definitions with detailed descriptions
def load_o1a_criteria(json_file_path):
    """Load O-1A criteria from JSON file
    
    Args:
        json_file_path: Path to the JSON file containing O-1A criteria definitions
        
    Returns:
        dict: Dictionary containing O-1A criteria definitions
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['o1a_criteria']
    except FileNotFoundError:
        logger.error(f"Criteria file not found: {json_file_path}")
        raise Exception(f"Criteria file not found: {json_file_path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in criteria file: {json_file_path}")
        raise Exception(f"Invalid JSON in criteria file: {json_file_path}")
    except KeyError:
        logger.error(f"Missing 'o1a_criteria' key in file: {json_file_path}")
        raise Exception(f"Missing 'o1a_criteria' key in file: {json_file_path}")
    except Exception as e:
        logger.error(f"Error loading criteria file: {str(e)}")
        raise Exception(f"Error loading criteria file: {str(e)}")
 

# Initialize the zero-shot classification pipeline with DeBERTa-v3
def init_zero_shot_pipeline():
    """Initialize the zero-shot classification pipeline with modern DeBERTa model"""
    logger.info("Initializing DeBERTa-v3 zero-shot classification pipeline")
    try:
        # Try the more powerful DeBERTa-v3-large model first
        return pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
            device=-1  # Use CPU
        )
    except Exception as e:
        logger.warning(f"Could not load large model, falling back to base model: {e}")
        try:
            # Fall back to the base model if the large one fails
            return pipeline(
                "zero-shot-classification",
                model="sileod/deberta-v3-base-tasksource-nli",
                device=-1  # Use CPU
            )
        except Exception as e:
            logger.error(f"Could not load DeBERTa models: {e}")
            # Last resort fallback to a smaller model
            return pipeline(
                "zero-shot-classification", 
                model="cross-encoder/nli-distilroberta-base",
                device=-1  # Use CPU
            )

# Document processing functions
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file"""
    try:
        logger.info(f"Extracting text from PDF: {file_path}")
        with fitz.open(file_path) as pdf:
            text = ""
            for page in pdf:
                text += page.get_text()
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Error processing PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file"""
    try:
        logger.info(f"Extracting text from DOCX: {file_path}")
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise Exception(f"Error processing DOCX: {str(e)}")

def extract_text_from_file(file_path: str) -> str:
    """Extract text from a file based on its extension"""
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        return extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        logger.info(f"Reading text file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise Exception(f"Unsupported file format: {file_extension}")

def prepare_cv_for_analysis(cv_text: str) -> List[LangchainDocument]:
    """
    Prepare the CV text for analysis by splitting it into manageable chunks
    and creating Langchain Document objects with metadata
    """
    logger.info("Preparing CV for analysis")
    # Split the CV into chunks for processing
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(cv_text)
    logger.info(f"Split CV into {len(chunks)} chunks")
    
    # Create Document objects with metadata
    documents = []
    for i, chunk in enumerate(chunks):
        # Determine section type based on content (simplified)
        section_type = "general"
        
        # Very simple section detection based on keywords
        lower_chunk = chunk.lower()
        if any(kw in lower_chunk for kw in ["education", "university", "degree", "phd", "master"]):
            section_type = "education"
        elif any(kw in lower_chunk for kw in ["experience", "work", "job", "position", "employment"]):
            section_type = "experience"
        elif any(kw in lower_chunk for kw in ["award", "honor", "prize", "recognition"]):
            section_type = "awards"
        elif any(kw in lower_chunk for kw in ["publication", "journal", "article", "paper", "conference"]):
            section_type = "publications"
        elif any(kw in lower_chunk for kw in ["skill", "proficiency", "expert", "competency"]):
            section_type = "skills"
        
        # Create a document with metadata
        doc = LangchainDocument(
            page_content=chunk,
            metadata={
                "chunk_id": i,
                "section_type": section_type,
                "char_count": len(chunk)
            }
        )
        documents.append(doc)
    
    return documents

def create_vector_store(documents: List[LangchainDocument]) -> FAISS:
    """Create a vector store from the CV documents for semantic searching"""
    logger.info("Creating vector store for semantic search")
    # Use HuggingFace embeddings instead of OpenAI
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

def analyze_criterion(criterion_key: str, criterion_info: dict, cv_documents: List[LangchainDocument], 
                      classifier, vector_store) -> Tuple[List[str], float, str]:
    """
    Analyze a specific O-1A criterion against the CV
    
    Args:
        criterion_key: Key identifier for the criterion
        criterion_info: Dictionary containing criterion details
        cv_documents: List of CV document chunks
        classifier: Zero-shot classification pipeline
        vector_store: Vector store for semantic search
        
    Returns:
        tuple: (matches, confidence, evaluation)
    """
    logger.info(f"Analyzing criterion: {criterion_info['name']}")
    
    # Perform semantic search to find relevant sections for this criterion
    query = f"{criterion_info['description']} examples achievements evidence"
    relevant_docs = vector_store.similarity_search(query, k=min(5, len(cv_documents)))
    
    # Extract relevant content
    relevant_content = [doc.page_content for doc in relevant_docs]
    
    matches = []
    scores = []
    
    # Process each relevant section with zero-shot classification
    for content in relevant_content:
        # Skip very short content
        if len(content.split()) < 10:
            continue
            
        # Classify the content against the criterion
        result = classifier(
            content, 
            candidate_labels=[
                f"Evidence of {criterion_info['name']}", 
                f"Not relevant to {criterion_info['name']}"
            ],
            hypothesis_template="This text describes {}."
        )
        
        # Check if it's a match
        if result['labels'][0].startswith("Evidence") and result['scores'][0] > 0.6:
            matches.append(content)
            scores.append(result['scores'][0])
    
    # Calculate confidence score
    confidence = max(scores) if scores else 0.0
    
    # Generate evaluation summary
    if confidence > 0.8:
        evaluation = f"Strong evidence found for {criterion_info['name']} criterion."
    elif confidence > 0.6:
        evaluation = f"Moderate evidence found for {criterion_info['name']} criterion."
    else:
        evaluation = f"Limited or no strong evidence found for {criterion_info['name']} criterion."
    
    return matches, confidence, evaluation

def evaluate_overall_qualification(criterion_assessments: Dict[str, CriterionAssessment]) -> Tuple[QualificationRating, str]:
    """
    Evaluate overall O-1A qualification based on criterion assessments
    
    Args:
        criterion_assessments: Dictionary of criterion assessments
        
    Returns:
        tuple: (rating, explanation)
    """
    logger.info("Evaluating overall qualification")
    
    # Count criteria with strong evidence (confidence > 0.7)
    strong_criteria = sum(1 for assessment in criterion_assessments.values() if assessment.confidence > 0.7)
    
    # Count criteria with moderate evidence (confidence > 0.6)
    moderate_criteria = sum(1 for assessment in criterion_assessments.values() 
                         if assessment.confidence > 0.6 and assessment.confidence <= 0.7)
    
    # Calculate average confidence
    avg_confidence = sum(assessment.confidence for assessment in criterion_assessments.values()) / len(criterion_assessments)
    
    # Determine rating
    if strong_criteria >= 4 and avg_confidence > 0.7:
        rating = QualificationRating.HIGH
        explanation = (
            f"Strong evidence found for {strong_criteria} out of 8 criteria. "
            f"According to USCIS guidelines, an applicant must satisfy at least 3 criteria to qualify. "
            f"With {strong_criteria} criteria strongly satisfied, the applicant appears to be a strong candidate."
        )
    elif (strong_criteria + moderate_criteria) >= 3 and avg_confidence > 0.6:
        rating = QualificationRating.MEDIUM
        explanation = (
            f"Moderate evidence found for at least 3 out of 8 criteria. "
            f"While the minimum requirement of 3 criteria appears to be met, the strength of evidence "
            f"suggests a moderate chance of qualification."
        )
    else:
        rating = QualificationRating.LOW
        explanation = (
            f"Limited evidence found for only {strong_criteria} out of 8 criteria with strong confidence. "
            f"USCIS requires applicants to satisfy at least 3 criteria with strong evidence. "
            f"The current evidence may not be sufficient for O-1A qualification."
        )
    
    return rating, explanation

def analyze_cv_for_o1a(file_path: str, criteria_json_path: str = "o1a_criteria.json") -> O1AAssessment:
    """
    Main function to analyze a CV file for O-1A visa qualification
    
    Args:
        file_path: Path to the CV file (PDF, DOCX, or TXT)
        criteria_json_path: Path to the JSON file containing O-1A criteria definitions
        
    Returns:
        O1AAssessment: Structured assessment of O-1A qualification
    """
    try:
        logger.info(f"Starting O-1A analysis for CV file: {file_path}")
        
        # Load O-1A criteria from JSON file
        o1a_criteria = load_o1a_criteria(criteria_json_path)
        logger.info(f"Successfully loaded {len(o1a_criteria)} criteria from {criteria_json_path}")
        
        # Extract text from CV file
        cv_text = extract_text_from_file(file_path)
        logger.info(f"Successfully extracted text from CV: {len(cv_text)} characters")
        
        # Prepare CV documents for analysis
        cv_documents = prepare_cv_for_analysis(cv_text)
        
        # Create vector store for semantic searching
        vector_store = create_vector_store(cv_documents)
        
        # Initialize zero-shot classification pipeline
        classifier = init_zero_shot_pipeline()
        
        # Analyze each criterion
        detailed_assessment = {}
        matches_by_criterion = {}
        
        for criterion_key, criterion_info in o1a_criteria.items():
            criterion_name = criterion_info["name"]
            
            # Format criterion info for analysis
            formatted_criterion = {
                "name": criterion_info["name"],
                "description": criterion_info["description"],
                "detailed_description": criterion_info["detailed_description"]
            }
            
            matches, confidence, evaluation = analyze_criterion(
                criterion_key, formatted_criterion, cv_documents, classifier, vector_store
            )
            
            # Store results
            detailed_assessment[criterion_name] = CriterionAssessment(
                matches=matches,
                confidence=confidence,
                evaluation=evaluation
            )
            
            matches_by_criterion[criterion_name] = matches
        
        # Evaluate overall qualification
        rating, explanation = evaluate_overall_qualification(detailed_assessment)
        
        # Create assessment object
        assessment = O1AAssessment(
            matches_by_criterion=matches_by_criterion,
            qualification_rating=rating,
            rating_explanation=explanation,
            detailed_assessment=detailed_assessment
        )
        
        logger.info(f"O-1A analysis complete: {assessment.qualification_rating}")
        return assessment
        
    except Exception as e:
        logger.error(f"Error in O-1A analysis: {str(e)}", exc_info=True)
        raise Exception(f"O-1A analysis failed: {str(e)}")
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python o1a_multiagent.py path/to/cv.pdf [output_file.json] [path/to/criteria.json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"o1a_assessment_{int(time.time())}.json"
    criteria_file = sys.argv[3] if len(sys.argv) > 3 else "o1a_criteria.json"
    
    print(f"Starting O-1A visa qualification assessment for: {file_path}")
    print(f"Using criteria definitions from: {criteria_file}")
    start_time = time.time()
    
    try:
        # Run the analysis
        assessment = analyze_cv_for_o1a(file_path, criteria_file)
        
        # Convert assessment to dictionary
        assessment_dict = assessment.to_dict()
        
        # Print summary to console
        print("\n" + "="*80)
        print("O-1A VISA QUALIFICATION ASSESSMENT")
        print("="*80)
        print(f"QUALIFICATION RATING: {assessment.qualification_rating.upper()}")
        print(f"EXPLANATION: {assessment.rating_explanation}")
        print("\nSTRONGEST CRITERIA:")
        
        # Sort criteria by confidence score
        sorted_criteria = sorted(
            [(name, assessment.detailed_assessment[name]) for name in assessment.matches_by_criterion.keys()],
            key=lambda x: x[1].confidence,
            reverse=True
        )
        
        # Print top 3 criteria
        for i, (criterion_name, criterion) in enumerate(sorted_criteria[:3], 1):
            print(f"{i}. {criterion_name} (Confidence: {criterion.confidence:.2f})")
            if criterion.matches:
                print(f"   Key evidence: {criterion.matches[0][:100]}...")
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assessment_dict, f, indent=2)
        print(f"\nDetailed assessment saved to: {output_file}")
        
        elapsed_time = time.time() - start_time
        print(f"\nAnalysis completed in {elapsed_time:.1f} seconds")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)