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

# class CompanyStartOfWeekIndex(GlobalSecondaryIndex):
#     """
#     GSI - company-start_of_week-index
#     """
#     class Meta:
#         index_name = 'company-start_of_week-index'
#         read_capacity_units = 5
#         write_capacity_units = 5
#         projection = AllProjection()
#     company        = UnicodeAttribute(hash_key=True)
#     start_of_week  = UnicodeAttribute(range_key=True)


class Bag(Model):
    """
    DynamoDB Table Config
    """
    class Meta:
        region = util_constants.REGION
        table_name = "diva-blp-bag"
        encrypted_fields = ["nric_sha"]
    bag_id = UnicodeAttribute(hash_key=True)
    color = UnicodeAttribute()
    weight = NumberAttribute()
    # activity_date = UnicodeAttribute(range_key=True)
    # company = UnicodeAttribute()
    # start_of_week = UnicodeAttribute()
    # location = UnicodeAttribute()
    # nric_sha = UnicodeAttribute()
    # company_startofweek_index = CompanyStartOfWeekIndex()
    # BooleanAttribute()
    # UTCDateTimeAttribute()


def setup_model(tablename: Optional[str] = None):
    return util_helper.setup_model(Bag, tablename)
