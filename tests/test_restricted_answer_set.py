import unittest

import basemodels.pydantic as pydantic_basemodels
import basemodels

from pydantic import ValidationError
from schematics.exceptions import DataError

MANIFEST_VALUES = {
    "job_mode": "batch",
    "request_type": "image_label_multiple_choice",
    "job_total_tasks": 0,
    "task_bid_price": -1,
    "oracle_stake": 0.05,
    "recording_oracle_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
    "reputation_oracle_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
    "reputation_agent_addr": "0x6a0E68eA5F706339dd6bd354F53EfcB5B9e53E49",
}

NESTED_MANIFEST_VALUES = {
    "request_type": "image_label_multiple_choice",
    "requester_question_example": "http://google.com/fake",  # fake url
}


def create_manifest_from_test_method(test_method, nested_manifest: bool, data: dict):
    if nested_manifest:
        data.update(NESTED_MANIFEST_VALUES)
    else:
        data.update(MANIFEST_VALUES)

    if test_method == "schematics":
        if nested_manifest:
            return basemodels.NestedManifest(data)
        else:
            return basemodels.Manifest(data)
    elif test_method == "pydantic":
        if nested_manifest:
            return pydantic_basemodels.NestedManifest.construct(**data)
        else:
            return pydantic_basemodels.Manifest.construct(**data)
    else:
        raise NotImplementedError(f"Test method {test_method} not implemented.")


def validate_manifest_from_test_method(test_method, manifest):
    if test_method == "schematics":
        manifest.validate()
    elif test_method == "pydantic":
        manifest.check()
    else:
        raise NotImplementedError(f"Test method {test_method} not implemented.")


def get_exception_type_from_test_method(test_method):
    if test_method == "schematics":
        return DataError
    elif test_method == "pydantic":
        return ValidationError
    else:
        raise NotImplementedError(f"Test method {test_method} not implemented.")


class TestILMCRequesterRestrictedAnswerSet(unittest.TestCase):
    """
    Tests that the restricted answer set is properly validated for ILMC challenges
    """

    def check_rsa_validation(self, test_method, rsa: dict, should_pass: bool, nested_manifest: bool = False):
        data = {"requester_restricted_answer_set": rsa}
        m = create_manifest_from_test_method(test_method, nested_manifest, data)
        if should_pass:
            validate_manifest_from_test_method(test_method, m)
        else:
            with self.assertRaises(get_exception_type_from_test_method(test_method)):
                validate_manifest_from_test_method(test_method, m)

    def test_schematics_one_option(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={"one": {"en": "one"}},
            should_pass=False
        )

    def test_schematics_one_option_nested(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={"one": {"en": "one"}},
            should_pass=False,
            nested_manifest=True
        )

    def test_schematics_two_options(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={"one": {"en": "one"}, "two": {"en": "two"}},
            should_pass=True
        )

    def test_schematics_two_options_nested(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={"one": {"en": "one"}, "two": {"en": "two"}},
            should_pass=True,
            nested_manifest=True
        )

    def test_schematics_five_options(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={
                "one": {"en": "one"},
                "two": {"en": "two"},
                "three": {"en": "three"},
                "four": {"en": "four"},
                "five": {"en": "five"}
            },
            should_pass=False
        )

    def test_schematics_five_options_nested(self):
        self.check_rsa_validation(
            test_method="schematics",
            rsa={
                "one": {"en": "one"},
                "two": {"en": "two"},
                "three": {"en": "three"},
                "four": {"en": "four"},
                "five": {"en": "five"}
            },
            should_pass=False,
            nested_manifest=True
        )

    def test_pydantic_one_option(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={"one": {"en": "one"}},
            should_pass=False
        )

    def test_pydantic_one_option_nested(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={"one": {"en": "one"}},
            should_pass=False,
            nested_manifest=True
        )

    def test_pydantic_two_options(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={"one": {"en": "one"}, "two": {"en": "two"}},
            should_pass=True
        )

    def test_pydantic_two_options_nested(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={"one": {"en": "one"}, "two": {"en": "two"}},
            should_pass=True,
            nested_manifest=True
        )

    def test_pydantic_five_options(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={
                "one": {"en": "one"},
                "two": {"en": "two"},
                "three": {"en": "three"},
                "four": {"en": "four"},
                "five": {"en": "five"}
            },
            should_pass=False
        )

    def test_pydantic_five_options_nested(self):
        self.check_rsa_validation(
            test_method="pydantic",
            rsa={
                "one": {"en": "one"},
                "two": {"en": "two"},
                "three": {"en": "three"},
                "four": {"en": "four"},
                "five": {"en": "five"}
            },
            should_pass=False,
            nested_manifest=True
        )
