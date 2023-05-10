from dataclasses import asdict, dataclass
from enum import Enum
import logging
import os
import datetime
import time
import base64
import string
import secrets
from typing import Any, List, Optional, Tuple
from uuid import UUID
from pynamodb.models import Model
import boto3

try:
    import util_constants
    from response import ApiGwResponse as Response
except ImportError:
    import sys

    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)
    sys.path.append(os.path.dirname(parentdir))

    from layer_diva.python import util_constants
    from layer_diva.python.response import ApiGwResponse as Response

DDB_CLIENT = boto3.client("dynamodb")
DDB_RES = boto3.resource("dynamodb")
KMS = boto3.session.Session().client("kms")
SSM = boto3.client("ssm")
DATE_TIME_TO_DICT_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger():
    """Returning Logger object"""
    log_obj = logging.getLogger()
    if log_obj.handlers:
        HANDLER = log_obj.handlers[0]
    else:
        HANDLER = logging.StreamHandler()
        log_obj.addHandler(HANDLER)
    LOG_FORMAT = (
        "[%(levelname)s] %(asctime)s- %(message)s (File %(pathname)s, Line %(lineno)s)"
    )
    HANDLER.setFormatter(logging.Formatter(LOG_FORMAT))
    log_obj.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))
    return log_obj


def get_time_now_obj():
    """Helper to get formatted time now in object"""
    return datetime.datetime.today() + datetime.timedelta(hours=8)

def get_epoch_time_ms():
    """Helper to get epoch time now"""
    time_now_ms = int(time.time() * 1000)  # epoch in milliseconds
    return str(time_now_ms)

def get_dt_now_str():
    """ Helper to get formatted time now as str for dt attributes"""
    return get_time_now_obj().strftime(util_constants.DATETIME_FORMAT)

def get_ttl(days):
    """ Helper to get TTL epoch time """
    return int((get_time_now_obj() + datetime.timedelta(days=days)).timestamp())

def encrypt_data(kms_key_id, field_list, fields_to_encrypt):
    """Encrypt selected field
    Args:
        kms_key_id: STR, id of the KMS key
        field_list: DICT, DICT to be encrypted,
            can contain fields that doesn't need encryption
        fields_to_encrypt: LIST, keys inside list of fields that need to be encrypted
    Returns:
        success: BOOL, whether success
    """
    for idx, key in enumerate(field_list):
        if key in fields_to_encrypt and field_list[key] != "":
            encrypted = KMS.encrypt(
                KeyId=kms_key_id,
                Plaintext=bytes(field_list[key], "utf-8"),
            )
            encrypted_value = base64.b64encode(encrypted["CiphertextBlob"]).decode(
                "utf-8"
            )
            field_list[key] = encrypted_value


def decrypt_data(field_list, fields_to_decrypt):
    """Encrypt selected field
    Args:
        field_list: DICT, dictionary with fields to be decrypted,
            can contain fields that doesn't need decryption
        fields_to_decrypt: LIST, keys inside list of fields that need to be decrypted
    Returns:
        success: BOOL, whether success
    """
    for idx, key in enumerate(field_list):
        if key in fields_to_decrypt and field_list[key] != "":
            decrypted = KMS.decrypt(
                CiphertextBlob=bytes(base64.b64decode(field_list[key]))
            )["Plaintext"].decode("utf-8")
            field_list[key] = decrypted


def clean_data_fields(data, field_list):
    """Clean up by returning only wanted field_list from the data_list
    Args:
        data: DICT, data to be clean up
        field_list: LIST, list of fields that should be returned
    """
    for k, v in list(data.items()):
        if k not in field_list:
            data.pop(k)
        elif isinstance(v, datetime.datetime):
            data[k] = v.strftime(util_constants.DATETIME_FORMAT)


def generate_random_pin(length):
    """Generate random pin (Uppercase alphabets + digits only) based on length
    Args:
        length: INT, length of the generated pin
    """
    pin_criteria = string.ascii_uppercase + string.digits
    random_pin = "".join(secrets.choice(pin_criteria) for i in range(length))

    return random_pin


def batch_writer(table_name, table_data):
    """Batch write data into DDB
    Args:
        table_name: STRING, name of table
        table_data: LIST, list of data to be inserted
    """
    table = DDB_RES.Table(table_name)
    with table.batch_writer() as writer:
        for item in table_data:
            writer.put_item(Item=item)

    return True


def setup_model(model: Model, table_name: Optional[str] = None):
    if table_name is not None:
        model.Meta.table_name = table_name
    if not model.exists():
        model.create_table(wait=True, billing_mode="PAY_PER_REQUEST")
    return model

def to_dict(obj: dataclass):
    return asdict(obj, dict_factory=_dict_factory)

def _dict_factory(data: List[Tuple[str, Any]]):
    return {
        field: _format_dataclass_field(value)
        for field, value in data
        }

def _format_dataclass_field(value):
    if isinstance(value, datetime.datetime):
        return value.strftime(DATE_TIME_TO_DICT_FORMAT)
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, Enum):
        return value.value
    else:
        return value
