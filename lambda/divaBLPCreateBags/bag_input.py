from dataclasses import dataclass, field
from typing import Optional

import util_constants


@dataclass
class BagInput:
    color: Optional[str]
    weight: Optional[float]
    bag_id: Optional[str]
