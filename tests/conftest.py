# -*- coding: utf-8 -*-
"""
Created on 2021-09-01T09:30
"""
from dataclasses import dataclass
from functools import reduce
import importlib
import re
from typing import Optional, Dict, List
import pytest
import os
import json
import boto3
import uuid
import base64
from moto import (
    mock_dynamodb,
    mock_cognitoidp,
    mock_ssm,
    mock_kms,
    mock_s3,
    mock_sns,
    mock_sqs,
)
from requests_mock import Mocker
from pathlib import Path
import responses
from tests.utils import load_file
from .deploy_layers import DeployLambdaLayers
from pytest_mock import mocker


@pytest.fixture(autouse=True, scope="session")
def setup_lambda_layers():
    """Mock AWS lambda layer deployment by moving layers from /lambda directory into the various lambda subdirectories.
    Removes layers after tests are completed."""
    deploy_layers = DeployLambdaLayers(["layer_diva"])
    yield


@pytest.fixture(autouse=True, scope="session")
def aws_credentials():
    # env for testing
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["POWERTOOLS_SERVICE_NAME"] = "Test-Service"
    os.environ["POWERTOOLS_METRICS_NAMESPACE"] = "Test-Metric-Namespace"


@pytest.fixture
def lambda_context():
    @dataclass
    class LambdaContext:
        function_name: str = "test"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:lambda:ap-southeast-1:809313241:function:test"
        )
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@pytest.fixture(autouse=True, scope="session")
def set_env_vars():
    # setting env vars
    os.environ["BOOKING_DB_NAME"] = "diva-blp-booking"
    os.environ["CORS"] = "*"
    os.environ["SNS_TOPIC"] = "test-topic"
    os.environ["BAG_DB_NAME"] = "diva-blp-bag"
    # to set env var for test function

@pytest.fixture(autouse=True, scope="session")
def kms_setup():
    with mock_kms():
        kms = boto3.client("kms")
        key = kms.create_key(Description="test data key")
        key_id = key["KeyMetadata"]["KeyId"]
        pytest.kms_key_id = key_id

        kms.generate_data_key(
            KeyId=key_id,
            NumberOfBytes=32,
        )

        yield kms


@pytest.fixture(autouse=True, scope="session")
def ddb_mock():
    with mock_dynamodb():
        dynamodb = boto3.client("dynamodb")

        yield dynamodb


@pytest.fixture(autouse=True, scope="function")
def ddb_client(ddb_mock, kms_setup):
    with mock_dynamodb():
        init_tables(ddb_mock, kms_setup)

        yield ddb_mock

        clear_tables(ddb_mock)


def clear_tables(dynamodb):
    for i in dynamodb.list_tables()["TableNames"]:
        dynamodb.delete_table(TableName=i)
    pytest.dynamodb = None


def init_tables(ddb_client, kms_setup):
    db_model_files = [
        f
        for f in os.listdir("lambda/layer_diva/python/models")
        if re.match(r".*\.py", f)
    ]
    models = [
        importlib.import_module(
            f"lambda.layer_diva.python.models.{file[:-3]}"
        ).setup_model()
        for file in db_model_files
    ]

    insert(
        ddb_client,
        kms_setup,
        "stubData/init_data.json",
        create_encrypted_fields_map(models),
    )


def insert(
    ddb_client,
    kms_setup,
    filename: str,
    encrypted_fields: Optional[Dict[str, List[str]]],
):
    for table, rows in load_file(filename).items():
        for row in rows:
            if (
                encrypted_fields is not None
                and encrypted_fields.get(table, None) is not None
            ):
                encrypt_data(row, kms_setup, encrypted_fields.get(table))
            ddb_client.put_item(TableName=table, Item=row)


def create_encrypted_fields_map(models):
    return reduce(
        lambda acc, model: {**acc, model.Meta.table_name: model.Meta.encrypted_fields},
        models,
        {},
    )


@pytest.fixture(scope="function")
def insert_data(ddb_client, kms_setup):
    def _insert_data(
        filename: str, encrpyt_fields: Optional[Dict[str, List[str]]] = None
    ):
        insert(ddb_client, kms_setup, filename, encrpyt_fields)

    return _insert_data


def encrypt_data(row, kms_setup_fix, encryption_fields):
    """Encrypt individual field
    Args:
        row: DICT, row to be inserted to DB
        kms_setup_fix: function, kms setup function
        encryption_fields: LIST, fields need to be encrypted
    """
    for key, val in row.items():
        val = val.get("S", "")
        if key in encryption_fields and val != "":
            encrypted = kms_setup_fix.encrypt(
                KeyId=pytest.kms_key_id, Plaintext=bytes(val, "utf-8")
            )

            encrypted_value = base64.b64encode(encrypted["CiphertextBlob"]).decode(
                "utf-8"
            )
            val = {"S": encrypted_value}
            row[key] = val
