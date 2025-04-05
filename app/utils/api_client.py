import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class APIClient:
    """
    A client for making API requests to external services.
    This can be used for automation tasks that need to interact with external APIs.
    """
    
    def __init__(self, base_url=None, api_key=None, timeout=30):
        """
        Initialize the API client.
        
        Args:
            base_url (str, optional): Base URL for the API
            api_key (str, optional): API key for authentication
            timeout (int, optional): Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def get(self, endpoint, params=None):
        """
        Make a GET request to the API.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            
        Returns:
            dict: Response data
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error making GET request to {url}: {str(e)}")
            return {"error": str(e)}
    
    def post(self, endpoint, data=None, json=None):
        """
        Make a POST request to the API.
        
        Args:
            endpoint (str): API endpoint
            data (dict, optional): Form data
            json (dict, optional): JSON data
            
        Returns:
            dict: Response data
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.post(url, data=data, json=json, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error making POST request to {url}: {str(e)}")
            return {"error": str(e)}
    
    def put(self, endpoint, data=None, json=None):
        """
        Make a PUT request to the API.
        
        Args:
            endpoint (str): API endpoint
            data (dict, optional): Form data
            json (dict, optional): JSON data
            
        Returns:
            dict: Response data
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.put(url, data=data, json=json, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error making PUT request to {url}: {str(e)}")
            return {"error": str(e)}
    
    def delete(self, endpoint, params=None):
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            
        Returns:
            dict: Response data
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.delete(url, params=params, timeout=self.timeout)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Error making DELETE request to {url}: {str(e)}")
            return {"error": str(e)}
    
    def _build_url(self, endpoint):
        """Build the full URL for the API request."""
        if self.base_url:
            return urljoin(self.base_url, endpoint)
        return endpoint
    
    def _handle_response(self, response):
        """Handle the API response."""
        try:
            response.raise_for_status()
            return response.json()
        except ValueError:
            # Response is not JSON
            return {"status_code": response.status_code, "text": response.text}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            try:
                error_data = response.json()
                return {"error": error_data, "status_code": response.status_code}
            except ValueError:
                return {"error": response.text, "status_code": response.status_code}
