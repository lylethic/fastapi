from enum import Enum


class BusinessType(str, Enum):
    ecommerce = "ecommerce"
    lead_generation = "lead_generation"
    subscription = "subscription"
    mobile_app = "mobile_app"
    service = "service"
    marketplace = "marketplace"
    digital_product = "digital_product"
    offline_business = "offline_business"
    hybrid = "hybrid"
    other = "other"
