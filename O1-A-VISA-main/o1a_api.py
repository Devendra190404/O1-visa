#!/usr/bin/env python
"""
O-1A visa assessment API using FastAPI
This implementation exposes the O-1A visa assessment functionality through a REST API.
"""

import os
import json
import logging
import tempfile
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum

# FastAPI for API
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the O-1A assessment functionality
from o1a_multiagent import (
    analyze_cv_for_o1a, 
    O1AAssessment, 
    QualificationRating,
    load_o1a_criteria
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("o1a_api")

# Define API models
class HealthResponse(BaseModel):
    status: str
    message: str

class CriterionInfo(BaseModel):
    name: str
    description: str
    detailed_description: str

class CriteriaResponse(BaseModel):
    status: str
    criteria: Dict[str, Dict[str, str]]

class CriterionAssessmentModel(BaseModel):
    matches: List[str]
    confidence: float
    evaluation: str

class AssessmentModel(BaseModel):
    matches_by_criterion: Dict[str, List[str]]
    qualification_rating: str
    rating_explanation: str
    detailed_assessment: Dict[str, CriterionAssessmentModel]

class AnalysisResponse(BaseModel):
    status: str
    assessment: Optional[AssessmentModel] = None
    message: Optional[str] = None

class BatchResultItem(BaseModel):
    filename: str
    status: str
    assessment: Optional[AssessmentModel] = None
    message: Optional[str] = None

class BatchAnalysisResponse(BaseModel):
    status: str
    results: List[BatchResultItem]

class StatsModel(BaseModel):
    total_analyses: int
    success_rate: float
    average_processing_time: float

class StatsResponse(BaseModel):
    status: str
    stats: StatsModel

class ErrorResponse(BaseModel):
    status: str
    message: str

# Configuration
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', tempfile.gettempdir())
CRITERIA_FILE = os.environ.get('O1A_CRITERIA_FILE', 'o1a_criteria.json')

# Initialize FastAPI app
app = FastAPI(
    title="O-1A Visa Assessment API",
    description="API for assessing qualification for O-1A visa category based on CV analysis",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with actual allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def cleanup_file(file_path: str):
    """Clean up temporary file"""
    try:
        os.remove(file_path)
        logger.info(f"Temporary file removed: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        # Try to load criteria file to verify system is ready
        load_o1a_criteria(CRITERIA_FILE)
        return HealthResponse(
            status="healthy",
            message="O-1A API is operational"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=HealthResponse(
                status="unhealthy",
                message=f"API is not fully operational: {str(e)}"
            ).dict()
        )

@app.get("/api/criteria", response_model=CriteriaResponse, tags=["Assessment"])
async def get_criteria():
    """Endpoint to get the O-1A criteria definitions"""
    try:
        criteria = load_o1a_criteria(CRITERIA_FILE)
        return CriteriaResponse(
            status="success",
            criteria=criteria
        )
    except Exception as e:
        logger.error(f"Failed to load criteria: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load criteria: {str(e)}"
        )

@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Assessment"])
async def analyze_cv(
    background_tasks: BackgroundTasks, 
    cv_file: UploadFile = File(...),
):
    """
    Analyze a CV for O-1A visa qualification
    
    - **cv_file**: The CV file (PDF, DOCX, or TXT format)
    
    Returns assessment results including qualification rating and detailed analysis.
    """
    # Check if a valid file was selected
    if cv_file.filename == '':
        raise HTTPException(
            status_code=400,
            detail="No file selected. Please select a valid file."
        )
    
    # Check if the file has an allowed extension
    if not allowed_file(cv_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Save the uploaded file
        filename = f"{int(time.time())}_{os.path.basename(cv_file.filename)}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Ensure directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Write the file content
        with open(file_path, 'wb') as f:
            content = await cv_file.read()
            if len(content) > MAX_CONTENT_LENGTH:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum allowed size is {MAX_CONTENT_LENGTH/(1024*1024)}MB."
                )
            f.write(content)
        
        logger.info(f"File saved to {file_path}")
        
        # Perform the O-1A analysis
        assessment = analyze_cv_for_o1a(file_path, CRITERIA_FILE)
        
        # Schedule cleanup of temporary file
        background_tasks.add_task(cleanup_file, file_path)
        
        # Convert assessment to dict
        assessment_dict = assessment.to_dict()
        
        return AnalysisResponse(
            status="success",
            assessment=assessment_dict
        )
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error analyzing CV: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze CV: {str(e)}"
        )

@app.post("/api/batch-analyze", response_model=BatchAnalysisResponse, tags=["Assessment"])
async def batch_analyze(
    background_tasks: BackgroundTasks,
    cv_files: List[UploadFile] = File(...),
):
    """
    Batch analyze multiple CVs for O-1A visa qualification
    
    - **cv_files**: List of CV files (PDF, DOCX, or TXT format)
    
    Returns assessment results for each file.
    """
    # Check if any valid files were selected
    if not cv_files or all(f.filename == '' for f in cv_files):
        raise HTTPException(
            status_code=400,
            detail="No files selected. Please select valid files."
        )
    
    results = []
    
    for cv_file in cv_files:
        if cv_file.filename == '':
            continue
            
        if not allowed_file(cv_file.filename):
            results.append(BatchResultItem(
                filename=cv_file.filename,
                status="error",
                message="Invalid file format"
            ))
            continue
        
        try:
            # Save the uploaded file
            filename = f"{int(time.time())}_{os.path.basename(cv_file.filename)}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Ensure directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Write the file content
            with open(file_path, 'wb') as f:
                content = await cv_file.read()
                if len(content) > MAX_CONTENT_LENGTH:
                    results.append(BatchResultItem(
                        filename=cv_file.filename,
                        status="error",
                        message=f"File too large. Maximum allowed size is {MAX_CONTENT_LENGTH/(1024*1024)}MB."
                    ))
                    continue
                f.write(content)
            
            # Perform the O-1A analysis
            assessment = analyze_cv_for_o1a(file_path, CRITERIA_FILE)
            
            # Schedule cleanup of temporary file
            background_tasks.add_task(cleanup_file, file_path)
            
            # Add the result
            results.append(BatchResultItem(
                filename=cv_file.filename,
                status="success",
                assessment=assessment.to_dict()
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing CV '{cv_file.filename}': {str(e)}")
            results.append(BatchResultItem(
                filename=cv_file.filename,
                status="error",
                message=f"Analysis failed: {str(e)}"
            ))
    
    return BatchAnalysisResponse(
        status="success",
        results=results
    )

@app.get("/api/stats", response_model=StatsResponse, tags=["System"])
async def get_stats():
    """Get API usage statistics"""
    # This is a placeholder - in a real implementation, you would track actual statistics
    return StatsResponse(
        status="success",
        stats=StatsModel(
            total_analyses=0,  # Placeholder
            success_rate=0.0,  # Placeholder
            average_processing_time=0.0  # Placeholder
        )
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='O-1A Visa Assessment API')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the API server on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the API server on')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--criteria', type=str, default='o1a_criteria.json', 
                        help='Path to the criteria JSON file')
    
    args = parser.parse_args()
    
    # Set criteria file
    CRITERIA_FILE = args.criteria
    
    # Print startup message
    print(f"Starting O-1A Visa Assessment API on {args.host}:{args.port}")
    print(f"Using criteria definitions from: {CRITERIA_FILE}")
    print(f"API documentation available at: http://{args.host}:{args.port}/docs")
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "o1a_api:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload
    )