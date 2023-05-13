from typing import Optional
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

try:
    import util_constants, util_helper
except ImportError:
    from layer_diva.python import util_constants, util_helper

class Bag(Model):
    """
    DynamoDB Table Config
    """
    class Meta:
        region = util_constants.REGION
        table_name = "diva-blp-bags"
        encrypted_fields = ["id"]
        # adding encrypted field due to test error; may need to modify conftest to remove call
    id = UnicodeAttribute(hash_key=True)
    color = UnicodeAttribute()
    weight = NumberAttribute()

def setup_model(tablename: Optional[str] = None):
    return util_helper.setup_model(Bag, tablename)
