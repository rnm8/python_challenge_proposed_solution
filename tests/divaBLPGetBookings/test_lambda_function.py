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
import sys, os
from responses import GET, POST
from freezegun import freeze_time
from tests.conftest import insert_data, lambda_context

from tests.utils import load_file

# Append Lambda folder to path so that Python can use relative imports
sys.path.append(os.path.abspath("../lambda/divaBLPGetBookings"))


@pytest.fixture(scope="class")
def get_lambda():
    return importlib.import_module("lambda.divaBLPGetBookings.lambda_function")

@pytest.fixture(scope="function")
def bag_details():
    return {
        "bag1": {"color": "red", "weight": 5000},
        "bag2": {"color": "blue", "weight": 10000},
    }


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

    def test_request(self, get_lambda, insert_data, lambda_context, bag_details):
        # load test_booking.json mock data for testing.
        insert_data(
        Path(__file__).parent / "data/test_booking.json",
        {"diva-blp-booking": ["nric_sha"]},
        )
    
        # mock bag data ("bag1", "bag2") with data for color and weight.
        # moved to top as a pytest fixture
        """
        bag_details = {
            "bag1": {"color": "red", "weight": 5000},
            "bag2": {"color": "blue", "weight": 10000},
        }        
        """

        # mock request with test details for company, and bags dict
        request_body = {
            "company": "CAG",
            "start_of_week": "2022-01-03",
            "location": "Airport",
            "bags": bag_details
        }

        # mock a HTTP request body
        request_body_json = json.dumps(request_body)

        # populate body of mock request.
        request = {
            "body": request_body_json,
        }

        # trigger mock request and context, and capture the response body
        response = get_lambda.lambda_handler(request, lambda_context)

        # reuse existing pattens to handle if response is a string
        if isinstance(response, str):
            body = json.loads(response["body"])
        else:
            body = response.get("body", {})

        # if correct, status code of 200 (indicating success) and a non-empty body
        assert response["statusCode"] == 200
        assert len(body) > 0