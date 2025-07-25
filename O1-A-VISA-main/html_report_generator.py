#!/usr/bin/env python
"""
HTML report generator for O-1A visa assessment.
This module generates a rich HTML report from O1A assessment results.
"""

import os
import json
from datetime import datetime
import logging
from typing import Dict, List, Any

logger = logging.getLogger("html_report_generator")

def generate_html_report(assessment, output_path):
    """
    Generate an HTML report from O1A assessment results
    
    Args:
        assessment: O1AAssessment object or dictionary
        output_path: Path to save the HTML report
    """
    logger.info(f"Generating HTML report: {output_path}")
    
    # Convert to dictionary if it's an object
    if not isinstance(assessment, dict):
        assessment = assessment.to_dict()
    
    # Extract data
    rating = assessment.get('qualification_rating', 'unknown').upper()
    rating_explanation = assessment.get('rating_explanation', '')
    approval_chance = assessment.get('approval_chance', 'Unknown')
    profile_type = assessment.get('profile_type', 'Unknown').replace('_', ' ').title()
    field_type = assessment.get('field_type', 'Unknown').title()
    criteria_met = assessment.get('criteria_met_count', 0)
    
    # Get detailed assessment
    detailed = assessment.get('detailed_assessment', {})
    
    # Sort criteria by confidence
    sorted_criteria = sorted(
        [(name, details) for name, details in detailed.items()],
        key=lambda x: x[1].get('confidence', 0),
        reverse=True
    )
    
    # Get recommendations and red flags
    recommendations = assessment.get('application_recommendations', [])
    red_flags = assessment.get('red_flags', [])
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O-1A Visa Assessment Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .report-date {{
            color: #666;
            font-size: 0.9em;
        }}
        .summary-box {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .rating {{
            display: inline-block;
            font-size: 1.2em;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
            margin-right: 15px;
        }}
        .rating-high {{
            background-color: #d4edda;
            color: #155724;
        }}
        .rating-medium {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .rating-low {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .approval-chance {{
            display: inline-block;
            font-weight: bold;
        }}
        .criteria-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .criterion-card {{
            flex: 1 0 350px;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .criterion-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .criterion-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .confidence-bar-container {{
            background-color: #eee;
            height: 8px;
            width: 100%;
            border-radius: 4px;
            margin-top: 10px;
        }}
        .confidence-bar {{
            height: 100%;
            border-radius: 4px;
        }}
        .confidence-high {{
            background-color: #28a745;
        }}
        .confidence-medium {{
            background-color: #ffc107;
        }}
        .confidence-low {{
            background-color: #dc3545;
        }}
        .criterion-evidence {{
            margin-top: 15px;
            font-size: 0.9em;
            max-height: 150px;
            overflow-y: auto;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .flags-box {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #dc3545;
        }}
        .recommendations-box {{
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #007bff;
        }}
        h2 {{
            color: #444;
            margin-top: 30px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        .section-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            background-color: #f5f5f5;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .meta-label {{
            font-weight: bold;
            margin-right: 5px;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>O-1A Visa Qualification Assessment Report</h1>
        <div class="report-date">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
    </div>
    
    <div class="summary-box">
        <h2>Executive Summary</h2>
        <div class="rating rating-{rating.lower()}">Rating: {rating}</div>
        <div class="approval-chance">Approval Chance: {approval_chance}</div>
        <p>{rating_explanation}</p>
        
        <div class="section-meta">
            <div class="meta-item">
                <span class="meta-label">Profile Type:</span> {profile_type}
            </div>
            <div class="meta-item">
                <span class="meta-label">Field:</span> {field_type}
            </div>
            <div class="meta-item">
                <span class="meta-label">Criteria Met:</span> {criteria_met}
            </div>
        </div>
    </div>
    
    <h2>Criteria Assessment</h2>
    <div class="criteria-list">
"""
    
    # Add criteria cards
    for name, details in sorted_criteria:
        confidence = details.get('confidence', 0)
        confidence_pct = int(confidence * 100)
        
        # Determine confidence class
        if confidence >= 0.7:
            confidence_class = "confidence-high"
        elif confidence >= 0.5:
            confidence_class = "confidence-medium"
        else:
            confidence_class = "confidence-low"
            
        # Get up to 2 evidence items
        evidence = details.get('matches', [])
        evidence_html = ""
        if evidence:
            evidence_html = "<div class='criterion-evidence'>"
            for i, ev in enumerate(evidence[:2]):
                # Truncate evidence text if too long
                ev_text = ev[:300] + "..." if len(ev) > 300 else ev
                evidence_html += f"<p><strong>Evidence {i+1}:</strong> {ev_text}</p>"
            evidence_html += "</div>"
            
        # Add any strong examples that were matched
        strong_examples = details.get('strong_examples_matched', [])
        if strong_examples:
            evidence_html += "<div style='margin-top:10px;font-size:0.9em;'>"
            evidence_html += f"<strong>Matched {len(strong_examples)} strong example(s):</strong> "
            examples_text = ", ".join(strong_examples[:2])
            if len(strong_examples) > 2:
                examples_text += f" and {len(strong_examples)-2} more"
            evidence_html += examples_text
            evidence_html += "</div>"
        
        html_content += f"""
        <div class="criterion-card">
            <div class="criterion-header">
                <div class="criterion-name">{name}</div>
                <div class="criterion-confidence">{confidence_pct}%</div>
            </div>
            <div class="confidence-bar-container">
                <div class="confidence-bar {confidence_class}" style="width: {confidence_pct}%;"></div>
            </div>
            <p>{details.get('evaluation', '')}</p>
            {evidence_html}
        </div>
    """
    
    html_content += """
    </div>
    """
    
    # Add red flags section if any
    if red_flags:
        html_content += """
    <h2>Potential Red Flags</h2>
    <div class="flags-box">
        <ul>
    """
        for flag in red_flags:
            flag_text = flag.get('flag', flag) if isinstance(flag, dict) else flag
            html_content += f"<li>{flag_text}</li>"
        
        html_content += """
        </ul>
    </div>
    """
    
    # Add recommendations section
    if recommendations:
        html_content += """
    <h2>Application Recommendations</h2>
    <div class="recommendations-box">
        <ol>
    """
        for rec in recommendations:
            html_content += f"<li>{rec}</li>"
        
        html_content += """
        </ol>
    </div>
    """
    
    # Add visa requirements section
    visa_reqs = assessment.get('visa_requirements', {})
    if visa_reqs:
        html_content += """
    <h2>Visa Requirements Summary</h2>
    <div class="summary-box">
    """
        
        # Add eligibility threshold
        threshold = visa_reqs.get('eligibility_threshold', '')
        if threshold:
            html_content += f"<p><strong>Eligibility Threshold:</strong> {threshold}</p>"
            
        # Add exception if any
        exception = visa_reqs.get('exception', '')
        if exception:
            html_content += f"<p><strong>Exception:</strong> {exception}</p>"
            
        # Add petition requirements
        petition_reqs = visa_reqs.get('petition_requirements', [])
        if petition_reqs:
            html_content += "<div><strong>Petition Requirements:</strong><ul>"
            for req in petition_reqs:
                html_content += f"<li>{req}</li>"
            html_content += "</ul></div>"
            
        # Add fees
        fees = visa_reqs.get('fees', {})
        if fees:
            html_content += "<div><strong>Fees:</strong><ul>"
            for fee_name, fee_amount in fees.items():
                html_content += f"<li>{fee_name.replace('_', ' ').title()}: {fee_amount}</li>"
            html_content += "</ul></div>"
            
        # Add visa duration
        duration = visa_reqs.get('visa_duration', {})
        if duration:
            html_content += "<div><strong>Visa Duration:</strong><ul>"
            for duration_type, duration_value in duration.items():
                html_content += f"<li>{duration_type.replace('_', ' ').title()}: {duration_value}</li>"
            html_content += "</ul></div>"
            
        html_content += """
    </div>
    """
    
    # Add footer
    html_content += """
    <div class="footer">
        <p>This report is generated by the O-1A Visa Assessment System and is for informational purposes only.</p>
        <p>It does not constitute legal advice. Please consult with an immigration attorney for professional guidance.</p>
    </div>
</body>
</html>
    """
    
    # Write the HTML to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML report saved to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving HTML report: {e}")
        raise
        
    return output_path

if __name__ == "__main__":
    import argparse
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate HTML report from O-1A assessment JSON")
    parser.add_argument("assessment_json", help="Path to the assessment JSON file")
    parser.add_argument("-o", "--output", help="Output HTML file path (default: based on input filename)")
    
    args = parser.parse_args()
    
    # Determine output path if not specified
    if not args.output:
        base_name = os.path.splitext(args.assessment_json)[0]
        args.output = f"{base_name}.html"
    
    # Load assessment from JSON
    with open(args.assessment_json, 'r', encoding='utf-8') as f:
        assessment = json.load(f)
    
    # Generate report
    output_path = generate_html_report(assessment, args.output)
    print(f"HTML report generated: {output_path}")