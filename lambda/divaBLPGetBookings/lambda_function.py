# -*- coding: utf-8 -*-
from dataclasses import dataclass
import os
import datetime

# We need to import the directory into the path for pytest to find the other files in the directory
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from api_response_handler import api_response_handler
from booking_input import BookingInput
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging.correlation_paths import API_GATEWAY_REST

from request_validation import parse_event
from util_helper import clean_data_fields, decrypt_data
from models.booking import Booking
from models.bag import Bag

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


@tracer.capture_lambda_handler
@api_response_handler
@log.inject_lambda_context(correlation_id_path=API_GATEWAY_REST, log_event=True)
def lambda_handler(event, context):
    booking_input = parse_event(event, BookingInput)
    bookings = find_relevant_bookings(booking_input)

    """
    assumption being made in this scenario is that a booking can have multiple bags and a bag can only belong to one booking
    """
    # check for body in event, else use empty dict
    if 'body' in event:
        body = event['body']
    else:
        body = {}
    
    # check for bags in body, else use empty dict again
    if 'bags' in body:
        bag_data = body['bags']
    else:
        bag_data = {}
        
    bags = {}

    # for each bag, put into dict
    for id, data in bag_data.items():
        bag = Bag(**data)
        bags[id] = bag

    # add bag to each booking
    for booking in bookings:
        booking_actions = [Booking.bags.set(bags)]
        booking.update(actions=booking_actions)

    return map_to_output(bookings)


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


def map_to_output(bookings: list[Booking]) -> list[dict]:
    booking_keys = ["company", "location", "capsule_id", "activity_date", "nric_sha"]
    fields_to_decrypt = ["nric_sha"]

    output = []
    for booking in bookings:
        booking_dict = booking.attribute_values
        clean_data_fields(booking_dict, booking_keys)
        decrypt_data(booking_dict, fields_to_decrypt)
        output.append(booking_dict)

    return output
