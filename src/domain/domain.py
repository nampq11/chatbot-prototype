from src.domain.exceptions import (
    DomainContextNotFound,
    DomainNameNotFound,
    DomainPerspectiveNotFound,
    DomainStyleNotFound,
)

from src.domain.extractor import BookingCareDomain

DOMAIN_NAMES = {
    "metal_health": "Metal Health",
    "healthcare": "Healthcare",
    "dermatology": "Dermatology",
}

DOMAIN_STYLES = {
    "metal_health": "Friendly and supportive",
    "healthcare": "Professional and informative",
    "dermatology": "Empathetic and understanding",
}

DOMAIN_PERSPECTIVES = {
    "metal_health": "Cognitive Behavioral Therapy (CBT)",
    "healthcare": "Patient-Centered Care",
    "dermatology": "Holistic Approach",
}

AVAILABLE_DOMAINS = list(DOMAIN_NAMES.keys())

class DomainFactory:
    @staticmethod
    def get_domain(id: str) -> BookingCareDomain:
        id_lower = id.lower()

        if id_lower not in DOMAIN_NAMES:
            raise DomainNameNotFound(id)
        
        if id_lower not in DOMAIN_STYLES:
            raise DomainStyleNotFound(id)
        
        if id_lower not in DOMAIN_PERSPECTIVES:
            raise DomainPerspectiveNotFound(id)
        
        return BookingCareDomain(
            id=id,
            name=DOMAIN_NAMES[id_lower],
            perspective=DOMAIN_PERSPECTIVES[id_lower],
            style=DOMAIN_STYLES[id_lower],
        )
    
    @staticmethod
    def get_available_domains() -> list[str]:
        return AVAILABLE_DOMAINS