class DomainException(Exception):
    """Base exception for all domain-specific errors."""
    pass


class PageNotFoundException(DomainException):
    """Raised when a LinkedIn page ID cannot be found in the database or via scraper."""
    
    def __init__(self, page_id: str):
        self.page_id = page_id
        super().__init__(f"LinkedIn Page with ID '{page_id}' not found.")


class ScrapingException(DomainException):
    """Raised when scraping fails due to network, format, or rate-limiting issues."""
    
    def __init__(self, page_id: str, reason: str):
        self.page_id = page_id
        self.reason = reason
        super().__init__(f"Failed to scrape LinkedIn page '{page_id}': {reason}")


class PostNotFoundException(DomainException):
    """Raised when a specific Post ID cannot be found."""
    
    def __init__(self, post_id: int):
        self.post_id = post_id
        super().__init__(f"Post with ID {post_id} not found.")

