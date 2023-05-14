# -*- coding: utf-8 -*-
"""
Created on 2021-09-01T09:30
"""
import pytest
import os
import json
import base64
import importlib
from pathlib import Path
import sys
import os
from responses import GET, POST
from freezegun import freeze_time

from tests.utils import load_file

# Append Lambda folder to path so that Python can use relative imports
sys.path.append(os.path.abspath("../lambda/divaBLPGetBookings"))


@pytest.fixture(scope="class")
def get_lambda():
    return importlib.import_module("lambda.divaBLPGetBookings.lambda_function")


# Note: freeze_time freezes the datetime at UTC time. Thus @freeze_time("2022-01-03") actually freezes time at
# 2022-01-03 08:00:00 GMT+8
@freeze_time("2022-01-03")
class TestGetBookings:
    def test_bad_request_body(self, get_lambda, lambda_context):
        request = {
            "body": json.dumps({"bad_param": "0000"}),
        }
        response = get_lambda.lambda_handler(request, lambda_context)
        assert response["statusCode"] == 400

    def test_valid(self, get_lambda, insert_data, lambda_context):
        insert_data(
            Path(__file__).parent / "data/test_booking.json",
            {"diva-blp-booking": ["nric_sha"]},
        )
        request = {
            "body": json.dumps(
                {"company": "CAG", "start_of_week": "2022-01-03", "location": "Airport"}
            ),
        }

        response = get_lambda.lambda_handler(request, lambda_context)
        body = response.get("body", {})
        if isinstance(response, str):
            body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert len(body) > 0

    def test_capsule_valid(self, get_lambda, insert_data, lambda_context):
        insert_data(Path(__file__).parent / "data/test_booking.json")
        request = {
            "body": json.dumps({"capsule_id": "888888"}),
        }

        response = get_lambda.lambda_handler(request, lambda_context)
        body = response.get("body", {})
        if isinstance(response, str):
            body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert len(body) > 0

    def test_scan(self, get_lambda, insert_data, lambda_context):
        insert_data(
            Path(__file__).parent / "data/test_booking.json",
            {"diva-blp-booking": ["nric_sha"]},
        )
        response_json = load_file(
            Path(__file__).parent / "response/booking_response.json"
        )

        request = {
            "body": json.dumps({}),
        }

        response = get_lambda.lambda_handler(request, lambda_context)
        body = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert body == response_json
