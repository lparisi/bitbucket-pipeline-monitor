"""
Bitbucket API client for the Pipeline Monitor.
"""
from typing import Dict, List, Optional, Any, Union
import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BitbucketAPIClient:
    """Client for interacting with the Bitbucket API."""
    
    BASE_URL = "https://api.bitbucket.org/2.0"
    
    def __init__(self) -> None:
        """Initialize the Bitbucket API client with credentials from environment variables."""
        self.username = os.getenv("BITBUCKET_USERNAME")
        self.app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        self.workspace = os.getenv("BITBUCKET_WORKSPACE")
        self.access_token = os.getenv("BITBUCKET_ACCESS_TOKEN")
        
        if not ((self.username and self.app_password) or (self.workspace and self.access_token)):
            raise ValueError(
                "Missing Bitbucket credentials. Please set BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD "
                "or BITBUCKET_WORKSPACE and BITBUCKET_ACCESS_TOKEN in your .env file."
            )
    
    def _get_auth_header(self) -> Dict[str, str]:
        """Get the authentication header for API requests."""
        if self.username and self.app_password:
            auth_str = f"{self.username}:{self.app_password}"
            encoded_auth = base64.b64encode(auth_str.encode()).decode()
            return {"Authorization": f"Basic {encoded_auth}"}
        elif self.workspace and self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        else:
            raise ValueError("No valid authentication method available")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Bitbucket API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body for POST/PUT requests
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_pipeline(self, repo_slug: str, pipeline_uuid: str) -> Dict[str, Any]:
        """
        Get details about a specific pipeline.
        
        Args:
            repo_slug: Repository slug in format workspace/repo-name
            pipeline_uuid: UUID of the pipeline
            
        Returns:
            Pipeline details
        """
        endpoint = f"repositories/{repo_slug}/pipelines/{pipeline_uuid}"
        return self._make_request("GET", endpoint)
    
    def get_latest_pipeline(self, repo_slug: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the latest pipeline for a repository.
        
        Args:
            repo_slug: Repository slug in format workspace/repo-name
            branch: Optional branch name to filter by
            
        Returns:
            Latest pipeline details
        """
        endpoint = f"repositories/{repo_slug}/pipelines/"
        params = {"sort": "-created_on"}
        
        if branch:
            params["target.ref_name"] = branch
        
        response = self._make_request("GET", endpoint, params=params)
        
        if not response.get("values"):
            raise ValueError(f"No pipelines found for repository {repo_slug}")
        
        # Return the first (latest) pipeline
        return response["values"][0]
    
    def get_pipeline_steps(self, repo_slug: str, pipeline_uuid: str) -> List[Dict[str, Any]]:
        """
        Get steps for a specific pipeline.
        
        Args:
            repo_slug: Repository slug in format workspace/repo-name
            pipeline_uuid: UUID of the pipeline
            
        Returns:
            List of pipeline steps
        """
        endpoint = f"repositories/{repo_slug}/pipelines/{pipeline_uuid}/steps/"
        response = self._make_request("GET", endpoint)
        return response.get("values", [])
    
    def get_pipeline_variables(self, repo_slug: str, pipeline_uuid: str) -> List[Dict[str, Any]]:
        """
        Get variables used in a specific pipeline.
        
        Args:
            repo_slug: Repository slug in format workspace/repo-name
            pipeline_uuid: UUID of the pipeline
            
        Returns:
            List of pipeline variables
        """
        endpoint = f"repositories/{repo_slug}/pipelines/{pipeline_uuid}/variables/"
        response = self._make_request("GET", endpoint)
        return response.get("values", [])
