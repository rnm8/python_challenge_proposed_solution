# -*- coding: utf-8 -*-
from typing import Optional
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import UnicodeAttribute, MapAttribute
from .bag import Bag

try:
    import util_constants, util_helper
except ImportError:
    from layer_diva.python import util_constants, util_helper

class CompanyStartOfWeekIndex(GlobalSecondaryIndex):
    """
    GSI - company-start_of_week-index
    """
    class Meta:
        index_name = 'company-start_of_week-index'
        read_capacity_units = 5
        write_capacity_units = 5
        projection = AllProjection()
    company        = UnicodeAttribute(hash_key=True) 
    start_of_week  = UnicodeAttribute(range_key=True)

class Booking(Model):
    """
    DynamoDB Table Config
    """
    class Meta:
        region = util_constants.REGION
        table_name = "diva-blp-booking"
        encrypted_fields = ["nric_sha"]
    capsule_id      = UnicodeAttribute(hash_key=True)
    activity_date   = UnicodeAttribute(range_key=True)
    company         = UnicodeAttribute()
    start_of_week   = UnicodeAttribute()
    location        = UnicodeAttribute()
    nric_sha        = UnicodeAttribute()
    company_startofweek_index  = CompanyStartOfWeekIndex()
    # BooleanAttribute() 
    # UTCDateTimeAttribute()
    bags = MapAttribute(of=Bag)
    """
    - Lists would not be efficient when accessing specific bag
    - Dict/Maps would be better aligned with use cases such as retrieving all bags under a single booking
    - DynamoDB is designed for key-value access patterns
    """
    
def setup_model(tablename: Optional[str] = None):
    return util_helper.setup_model(Booking, tablename)