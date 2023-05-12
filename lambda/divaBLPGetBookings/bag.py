from dataclasses import dataclass

@dataclass
class Bag:
    id: str
    color: str
    weight: float
    """
    - color is not treated as optional, as it would make human identification of bags more difficult
    - float to ensure accuracy in grams for baggage weighing
    - will require manual conversion, so need to use pynamodb model instead for automatic conversion 
    """