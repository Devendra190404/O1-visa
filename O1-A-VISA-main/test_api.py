import requests
import sys
import json
from pathlib import Path

def test_o1a_assessment(cv_file_path, api_url="http://localhost:8000"):
    """
    Test the O-1A assessment API with a CV file
    
    
    Args:
        cv_file_path (str): Path to the CV file
        api_url (str): Base URL of the API
    """
    # Check if file exists
    file_path = Path(cv_file_path)
    if not file_path.exists():
        print(f"Error: File {cv_file_path} does not exist")
        sys.exit(1)
    
    # Prepare the file for upload
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "application/octet-stream")}
        
        # Send request to API
        print(f"Sending CV to {api_url}/assess-o1a-qualification...")
        try:
            response = requests.post(f"{api_url}/assess-o1a-qualification", files=files)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                # Pretty print the assessment
                print("\n--- O-1A VISA QUALIFICATION ASSESSMENT ---\n")
                
                print(f"QUALIFICATION RATING: {result['qualification_rating'].upper()}")
                print(f"EXPLANATION: {result['rating_explanation']}")
                
                print("\nQUALIFYING ITEMS BY CRITERION:")
                for criterion, matches in result["matches_by_criterion"].items():
                    if matches:
                        print(f"\n{criterion}:")
                        for i, match in enumerate(matches, 1):
                            print(f"  {i}. {match.strip()}")
                    else:
                        print(f"\n{criterion}: No qualifying items found")
                
                # Save result to file
                output_file = file_path.stem + "_assessment.json"
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                    
                print(f"\nAssessment saved to {output_file}")
                
            else:
                print(f"Error: API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.RequestException as e:
            print(f"Error connecting to API: {e}")
            print("Make sure the API server is running at the specified URL")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_cv_file> [api_url]")
        sys.exit(1)
    
    cv_file_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    test_o1a_assessment(cv_file_path, api_url)