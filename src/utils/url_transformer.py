"""
Utility for URL transformations.
"""
import re

class UrlTransformer:
    """
    Handles transformation of Zoom URLs to different formats.
    """
    
    # Regex pattern to extract meeting ID and password from standard invite links
    ZOOM_INVITE_PATTERN = r"https://([\w\-\.]+)/j/(\d+)\?pwd=([\w\-\.]+)"

    @staticmethod
    def to_web_client(url: str) -> str:
        """
        Convert standard Zoom invite URL to Web Client format.
        
        Input: https://{organization}.zoom.us/j/92722383681?pwd=H7PA...
        Output: https://{domain}/wc/{meeting_id}/join?pwd={token}
        
        Args:
            url: Original Zoom meeting URL
            
        Returns:
            Transformed Web Client URL or original if pattern doesn't match.
        """
        match = re.search(UrlTransformer.ZOOM_INVITE_PATTERN, url)
        
        if match:
            domain, meeting_id, pwd = match.groups()
            return f"https://{domain}/wc/{meeting_id}/join?pwd={pwd}"
        
        return url
