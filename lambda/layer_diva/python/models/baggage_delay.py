# -*- coding: utf-8 -*-
from typing import Optional
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, TTLAttribute, MapAttribute, NumberAttribute, ListAttribute

try:
    import util_constants, util_helper
except ImportError:
    from layer_diva.python import util_constants, util_helper

class DelayMap(MapAttribute):
    """
    Sub class for the flight mapping to parse the information
    coming out of dynamodb
    """
    delay_type = UnicodeAttribute(null=False)
    duration = NumberAttribute(null=True)
    reason = UnicodeAttribute(null=True)
    timestamp = UnicodeAttribute(null=False)

class BaggageDelay(Model):
    class Meta:
        region = util_constants.REGION
        table_name = "diva-pbe-baggage-delays"
        encrypted_fields = None

    flight_no = UnicodeAttribute(hash_key=True)
    scheduled_dt = UnicodeAttribute(range_key=True)
    delays = ListAttribute(of=DelayMap)
    ttl = TTLAttribute()

def setup_model(tablename: Optional[str] = None):
    return util_helper.setup_model(BaggageDelay, tablename)