# -*- coding: utf-8 -*-
from models.booking import Booking
from models.bag import Bag
from util_helper import clean_data_fields, decrypt_data
from request_validation import parse_event
from aws_lambda_powertools.logging.correlation_paths import API_GATEWAY_REST
from aws_lambda_powertools import Logger, Tracer


from api_response_handler import api_response_handler
from dataclasses import dataclass
import os
import datetime


# We need to import the directory into the path for pytest to find the other files in the directory
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from bag_input import BagInput  # nopep8
from booking_input import BookingInput  # nopep8

# Initialize env vars
CORS = os.environ["CORS"].strip()

log = Logger()
tracer = Tracer()


@dataclass
class BookingInput:
    company: Optional[str]
    start_of_week: Optional[str]
    location: Optional[str]
    capsule_id: Optional[str]


@dataclass
class BagInput:
    color: Optional[str]
    weight: Optional[float]
    bag_id: Optional[str]


@tracer.capture_lambda_handler
@api_response_handler
@log.inject_lambda_context(correlation_id_path=API_GATEWAY_REST, log_event=True)
def lambda_handler(event, context):
    # booking_input = parse_event(event, BookingInput)
    # bookings = find_relevant_bookings(booking_input)
    bag_input = parse_event(event, BagInput)
    bags = find_bags(bag_input)

    return map_to_output(bags)


def find_relevant_bookings(booking_input: BookingInput) -> list[Booking]:
    if booking_input.capsule_id:
        bookings = Booking.query(booking_input.capsule_id)
    elif booking_input.company:
        bookings = Booking.company_startofweek_index.query(
            booking_input.company,
            Booking.start_of_week == booking_input.start_of_week,
            Booking.location == booking_input.location,
        )
    else:
        bookings = Booking.scan()

    return list(bookings)


def find_bags(bag_input: BagInput) -> list[Bag]:

    bags = Bag.scan()

    return list(bags)


def map_to_output(bags: list[Bag]) -> list[dict]:
    bag_keys = ["bag_id", "color", "weight"]
    # fields_to_decrypt = ["nric_sha"]

    output = []
    for bag in bags:
        bag_dict = bag.attribute_values
        clean_data_fields(bag_dict, bag_keys)
        # decrypt_data(booking_dict, fields_to_decrypt)
        output.append(bag_dict)

    return output
