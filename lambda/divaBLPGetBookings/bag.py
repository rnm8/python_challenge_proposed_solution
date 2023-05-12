from dataclasses import dataclass

@dataclass
class Bag:
    id: str
    color: str
    weight: float
    """
    to ensure accuracy in grams for baggage weighing
    """