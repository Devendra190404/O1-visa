#!/usr/bin/env python
"""
Client library for the O-1A Visa Assessment API
This provides a simple Python client to interact with the API
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

class O1AApiClient:
    """Client for interacting with the O-1A Visa Assessment API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the O-1A API server
        """
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the API is healthy and operational
        
        Returns:
            dict: Response containing health status
        
        Raises:
            requests.RequestException: If the request fails
        """
        response = requests.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()
    
    def get_criteria(self) -> Dict[str, Any]:
        """
        Retrieve the O-1A criteria definitions
        
        Returns:
            dict: O-1A criteria definitions
        
        Raises:
            requests.RequestException: If the request fails
        """
        response = requests.get(f"{self.base_url}/api/criteria")
        response.raise_for_status()
        return response.json()
    
    def analyze_cv(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Analyze a CV file for O-1A visa qualification
        
        Args:
            file_path: Path to the CV file (PDF, DOCX, or TXT)
        
        Returns:
            dict: Assessment results
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file has an unsupported format
            requests.RequestException: If the API request fails
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file extension
        if file_path.suffix.lower() not in ['.pdf', '.docx', '.txt']:
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Supported formats: .pdf, .docx, .txt")
        
        # Prepare the file for upload
        with open(file_path, 'rb') as f:
            files = {'cv_file': (file_path.name, f, self._get_mime_type(file_path.suffix))}
            
            # Send the request
            response = requests.post(f"{self.base_url}/api/analyze", files=files)
            response.raise_for_status()
            
        return response.json()
    
    def batch_analyze(self, file_paths: List[Union[str, Path]]) -> Dict[str, Any]:
        """
        Analyze multiple CV files for O-1A visa qualification
        
        Args:
            file_paths: List of paths to CV files (PDF, DOCX, or TXT)
        
        Returns:
            dict: Assessment results for each file
        
        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If any file has an unsupported format
            requests.RequestException: If the API request fails
        """
        if not file_paths:
            raise ValueError("No files provided for batch analysis")
        
        files = []
        
        # Prepare each file for upload
        for file_path in file_paths:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file extension
            if file_path.suffix.lower() not in ['.pdf', '.docx', '.txt']:
                raise ValueError(f"Unsupported file format: {file_path.suffix}. Supported formats: .pdf, .docx, .txt")
            
            # Add to files list
            with open(file_path, 'rb') as f:
                files.append(('cv_files[]', (file_path.name, f, self._get_mime_type(file_path.suffix))))
        
        # Send the request
        response = requests.post(f"{self.base_url}/api/batch-analyze", files=files)
        response.raise_for_status()
        
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics
        
        Returns:
            dict: API usage statistics
        
        Raises:
            requests.RequestException: If the request fails
        """
        response = requests.get(f"{self.base_url}/api/stats")
        response.raise_for_status()
        return response.json()
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type for a file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain'
        }
        return mime_types.get(extension.lower(), 'application/octet-stream')

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python o1a_api_client.py path/to/cv.pdf [api_url]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print(f"Connecting to O-1A API at: {api_url}")
    client = O1AApiClient(api_url)
    
    try:
        # Check if the API is up
        health = client.health_check()
        print(f"API Status: {health['status']}")
        
        # Analyze the CV
        print(f"Analyzing CV: {file_path}")
        result = client.analyze_cv(file_path)
        
        if result['status'] == 'success':
            assessment = result['assessment']
            print("\n" + "="*80)
            print("O-1A VISA QUALIFICATION ASSESSMENT")
            print("="*80)
            print(f"QUALIFICATION RATING: {assessment['qualification_rating'].upper()}")
            print(f"EXPLANATION: {assessment['rating_explanation']}")
            
            # Print top criteria
            print("\nTOP CRITERIA:")
            detailed = {name: details for name, details in assessment['detailed_assessment'].items()}
            sorted_criteria = sorted(detailed.items(), key=lambda x: x[1]['confidence'], reverse=True)
            
            for i, (criterion_name, criterion) in enumerate(sorted_criteria[:3], 1):
                print(f"{i}. {criterion_name} (Confidence: {criterion['confidence']:.2f})")
                if criterion['matches']:
                    print(f"   Key evidence: {criterion['matches'][0][:100]}...")
            
        else:
            print(f"Analysis failed: {result['message']}")
        
    except requests.RequestException as e:
        print(f"API request failed: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
