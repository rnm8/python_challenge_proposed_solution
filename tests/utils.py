import csv
from dataclasses import dataclass
import json
from pathlib import Path
from unittest import TestCase


def load_csv(filename: str):
    with open(
        Path(__file__).parent / filename, newline=""
    ) as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        return list(reader)

def load_file(filename: str):
    file_to_load = Path(__file__).parent / filename
    file_content = {}
    with file_to_load.open() as json_file:
        file_content = json.load(json_file)
    return file_content

def load_file_raw(filename: str):
    file_to_load = Path(__file__).parent / filename
    with file_to_load.open() as file:
        file_content = file.read()
    return file_content


test_case = TestCase()
test_case.max_diff = None

@dataclass
class MockResponse:
    status = 200
    headers = {}
    body = ""

    def json(self):
        return self.body

def dict_to_lambda_event(data: dict):
    return {
        "body": json.dumps(data)
    }