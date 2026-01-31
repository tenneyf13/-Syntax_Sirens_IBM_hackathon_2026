"""
Watson Orchestrate Service Module
Handles communication with Watson Orchestrate agent for WCAG analysis
"""

import os
import requests
from typing import Tuple, Dict, Any
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WatsonOrchestrateService:
    """Service class for Watson Orchestrate integration"""
    
    def __init__(self):
        self.api_key = os.getenv("IBM_CLOUD_API_KEY")
        self.agent_id = os.getenv("WATSON_ORCHESTRATE_AGENT_ID", "638256ff-9626-4012-bb71-0a111f64ecf9")
        self.host_url = os.getenv("WATSON_ORCHESTRATE_HOST_URL", "https://dl.watson-orchestrate.ibm.com")
        self.instance_id = os.getenv("WATSON_ORCHESTRATE_INSTANCE_ID", "20260130-1647-0257-7054-5539941574fb")
        
        if not self.api_key:
            raise ValueError("IBM_CLOUD_API_KEY not found in environment variables")
        
        self.authenticator = IAMAuthenticator(self.api_key)
        self._token = None
    
    def _get_token(self) -> str:
        """Get or refresh IBM Cloud IAM token"""
        if not self._token:
            self._token = self.authenticator.token_manager.get_token()
        return self._token
    
    def analyze_wcag(self, html_content: str, url: str = "") -> Tuple[str, str]:
        """
        Analyze HTML content for WCAG compliance using Watson Orchestrate agent
        
        Args:
            html_content: The HTML content to analyze
            url: Optional URL of the page being analyzed
            
        Returns:
            Tuple of (findings, recommendations)
        """
        try:
            token = self._get_token()
            
            # Prepare the analysis request
            prompt = self._create_wcag_prompt(html_content, url)
            
            # Call Watson Orchestrate agent
            response = self._call_agent(token, prompt)
            
            # Parse the response
            findings, recommendations = self._parse_agent_response(response)
            
            return findings, recommendations
            
        except Exception as e:
            # Return error information in a user-friendly format
            error_msg = f"Error analyzing WCAG compliance: {str(e)}"
            return error_msg, "Please check your Watson Orchestrate configuration and try again."
    
    def _create_wcag_prompt(self, html_content: str, url: str = "") -> str:
        """Create a detailed prompt for WCAG analysis"""
        prompt = f"""Analyze the following HTML content for WCAG 2.1 Level AA compliance.

URL: {url if url else 'Not provided'}

Please provide:
1. A list of WCAG compliance issues found
2. Specific recommendations for fixing each issue
3. Priority level for each issue (Critical, High, Medium, Low)

Focus on:
- Missing alt text for images
- Color contrast issues
- Missing form labels
- Keyboard accessibility
- Semantic HTML structure
- ARIA attributes
- Heading hierarchy

HTML Content:
{html_content[:5000]}  # Limit to first 5000 chars to avoid token limits

Please format your response in two clear sections:
FINDINGS: (list all issues found)
RECOMMENDATIONS: (provide specific fixes for each issue)
"""
        return prompt
    
    def _call_agent(self, token: str, prompt: str) -> Dict[str, Any]:
        """
        Call Watson Orchestrate agent with the analysis prompt
        
        Note: The exact API endpoint may vary based on your Watson Orchestrate setup.
        This implementation tries multiple common patterns.
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Try primary endpoint pattern
        api_url = f"{self.host_url}/api/v1/instances/{self.instance_id}/agents/{self.agent_id}/run"
        
        payload = {
            "input": {
                "message": prompt
            }
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            
            # If primary endpoint fails, try alternative chat endpoint
            api_url = f"{self.host_url}/api/chat/v1/agents/{self.agent_id}/messages"
            payload = {"message": prompt}
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            
            # If both fail, raise an error with details
            raise Exception(f"Watson Orchestrate API error: {response.status_code} - {response.text}")
            
        except requests.exceptions.Timeout:
            raise Exception("Watson Orchestrate request timed out. The agent may be processing a large request.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error calling Watson Orchestrate: {str(e)}")
    
    def _parse_agent_response(self, response: Dict[str, Any]) -> Tuple[str, str]:
        """
        Parse the Watson Orchestrate agent response into findings and recommendations
        
        The response format may vary based on your agent configuration.
        This method handles common response patterns.
        """
        # Try to extract the agent's response text
        response_text = ""
        
        # Common response patterns
        if "output" in response:
            if isinstance(response["output"], dict):
                response_text = response["output"].get("text", "") or response["output"].get("message", "")
            else:
                response_text = str(response["output"])
        elif "message" in response:
            response_text = response["message"]
        elif "result" in response:
            response_text = response["result"]
        elif "text" in response:
            response_text = response["text"]
        else:
            # If we can't find a standard field, use the whole response
            response_text = str(response)
        
        # Split into findings and recommendations
        findings = ""
        recommendations = ""
        
        # Look for section markers in the response
        if "FINDINGS:" in response_text and "RECOMMENDATIONS:" in response_text:
            parts = response_text.split("RECOMMENDATIONS:")
            findings = parts[0].replace("FINDINGS:", "").strip()
            recommendations = parts[1].strip()
        elif "findings" in response_text.lower() and "recommendations" in response_text.lower():
            # Try case-insensitive split
            lower_text = response_text.lower()
            findings_idx = lower_text.find("findings")
            rec_idx = lower_text.find("recommendations")
            
            if findings_idx < rec_idx:
                findings = response_text[findings_idx:rec_idx].strip()
                recommendations = response_text[rec_idx:].strip()
            else:
                findings = response_text[:rec_idx].strip()
                recommendations = response_text[rec_idx:].strip()
        else:
            # If no clear sections, split the response in half
            mid_point = len(response_text) // 2
            findings = response_text[:mid_point].strip()
            recommendations = response_text[mid_point:].strip()
        
        # Ensure we have some content
        if not findings:
            findings = "Analysis completed. See recommendations for details."
        if not recommendations:
            recommendations = response_text if response_text else "No specific recommendations generated."
        
        return findings, recommendations


# Create a singleton instance
_service_instance = None

def get_watson_orchestrate_service() -> WatsonOrchestrateService:
    """Get or create the Watson Orchestrate service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = WatsonOrchestrateService()
    return _service_instance