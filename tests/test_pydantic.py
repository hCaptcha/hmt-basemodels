from unittest import TestCase, mock
from copy import deepcopy

from pydantic.error_wrappers import ValidationError
from basemodels.pydantic import Manifest


SIMPLE = {
    "job_mode": "batch",
    "request_type": "image_label_multiple_choice",
    "requester_accuracy_target": 0.8,
    "requester_description": "pyhcaptcha internal_id: 69efdbe1-e586-42f8-bf05-a5745f75402a",
    "requester_max_repeats": 7,
    "requester_min_repeats": 3,
    "requester_question": {"en": "deploy to only certain sites"},
    "requester_restricted_answer_set": {"one": {"en": "one"}},
    "task_bid_price": -1,
    "unsafe_content": False,
    "oracle_stake": 0.05,
    "recording_oracle_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
    "reputation_oracle_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
    "reputation_agent_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
    "groundtruth_uri": "https://hmt-jovial-lamport.hcaptcha.com/pyhcaptcha-client/taskdata/sha1:bf21a9e8fbc5a3846fb05b4fa0859e0917b2202f.json",
    "taskdata_uri": "https://hmt-jovial-lamport.hcaptcha.com/pyhcaptcha-client/taskdata/sha1:97d170e1550eee4afc0af065b78cda302a97674c.json",
    "job_total_tasks": 0,
    "job_api_key": "417714f0-7ce6-412b-b394-0d2ae58a8c6d",
    "restricted_audience": {
        "sitekey": [
            {"dfe03e7c-f417-4726-8b14-ae033a3cc66e": {"score": 1}},
            {"dfe03e7c-f417-4726-8b12-ae033a3cc66a": {"score": 1}},
        ]
    },
}


class PydanticTest(TestCase):
    def setUp(self):
        self.m = deepcopy(SIMPLE)

    def test_example_err(self):
        self.m["requester_question_example"] = []
        with self.assertRaises(ValidationError):
            Manifest.parse_obj(self.m)

    def test_working(self):
        Manifest.parse_obj(self.m)

    def test_unique_id(self):
        m1 = deepcopy(SIMPLE)
        m2 = deepcopy(SIMPLE)
        self.assertNotEqual(str(Manifest(**m1).job_id), str(Manifest(**m2).job_id))
