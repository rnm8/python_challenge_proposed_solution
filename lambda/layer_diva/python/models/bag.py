# -*- coding: utf-8 -*-
from typing import Optional
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

try:
    import util_constants
    import util_helper
except ImportError:
    from layer_diva.python import util_constants, util_helper

# class BagColorWeight(GlobalSecondaryIndex):
#     """
#     GSI - bag-color-weight
#     """
#     class Meta:
#         index_name = 'bag-color-weight'
#         read_capacity_units = 1
#         write_capacity_units = 1
#         projection = AllProjection()
#         #set to minimum read/write capacity; need to configure auto-scaling
#     bag_id = UnicodeAttribute(hash_key=True)
#     color = UnicodeAttribute(range_key=True)
#     weight - NumberAttribute(range_key=True)


class Bag(Model):
    """
    DynamoDB Table Config for Bag
    """
    class Meta:
        region = util_constants.REGION
        table_name = "diva-blp-bag"
        encrypted_fields = ["nric_sha"]
    bag_id = UnicodeAttribute(hash_key=True)
    color = UnicodeAttribute()
    weight = NumberAttribute()

def setup_model(tablename: Optional[str] = None):
    return util_helper.setup_model(Bag, tablename)
