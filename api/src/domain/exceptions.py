class DomainNameNotFound(Exception):
    """Exception raised when a domain name is not found."""
    def __init__(self, domain_id: str):
        self.message = f"Domain name for {domain_id} not found."
        super().__init__(self.message)

class DomainPerspectiveNotFound(Exception):
    """Exception raised when a domain perspective is not found."""
    def __init__(self, domain_id: str):
        self.message = f"Domain perspective for {domain_id} not found."
        super().__init__(self.message)
    
class DomainStyleNotFound(Exception):
    """Exception raised when a domain style is not found."""
    def __init__(self, domain_id: str):
        self.message = f"Domain style for {domain_id} not found."
        super().__init__(self.message)

class DomainContextNotFound(Exception):
    """Exception raised when a domain context is not found."""
    def __init__(self, domain_id: str):
        self.message = f"Domain context for {domain_id} not found."
        super().__init__(self.message)
