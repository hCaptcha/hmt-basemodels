#!/usr/bin/env python3

import logging
import os
import sys
import schematics
import basemodels
import unittest

CALLBACK_URL = "http://google.com/webback"
FAKE_URL = "http://google.com/fake"
IMAGE_LABEL_BINARY = "image_label_binary"

REP_ORACLE = "0x61F9F0B31eacB420553da8BCC59DC617279731Ac"
REC_ORACLE = "0xD979105297fB0eee83F7433fC09279cb5B94fFC6"
FAKE_ORACLE = "0x1413862c2b7054cdbfdc181b83962cb0fc11fd92"


def a_manifest(number_of_tasks=100,
               bid_amount=1.0,
               oracle_stake=0.05,
               expiration_date=0,
               minimum_trust=.1,
               request_type=IMAGE_LABEL_BINARY,
               request_config=None,
               job_mode='batch',
               multi_challenge_manifests=None) -> basemodels.Manifest:
    model = {
        'requester_restricted_answer_set': {
            '0': {
                'en': 'English Answer 1'
            },
            '1': {
                'en': 'English Answer 2',
                'answer_example_uri': 'https://hcaptcha.com/example_answer2.jpg'
            }
        },
        'job_mode': job_mode,
        'request_type': request_type,
        'multi_challenge_manifests': multi_challenge_manifests,
        'unsafe_content': False,
        'task_bid_price': bid_amount,
        'oracle_stake': oracle_stake,
        'expiration_date': expiration_date,
        'minimum_trust_server': minimum_trust,
        'minimum_trust_client': minimum_trust,
        'requester_accuracy_target': minimum_trust,
        'recording_oracle_addr': REC_ORACLE,
        'reputation_oracle_addr': REP_ORACLE,
        'reputation_agent_addr': REP_ORACLE,
        'instant_result_delivery_webhook': CALLBACK_URL,
        'requester_question': {
            "en": "How much money are we to make"
        },
        'requester_question_example': FAKE_URL,
        'job_total_tasks': number_of_tasks,
        'taskdata_uri': FAKE_URL
    }

    if request_config:
        model.update({'request_config': request_config})

    manifest = basemodels.Manifest(model)
    manifest.validate()

    return manifest


def a_nested_manifest(request_type=IMAGE_LABEL_BINARY, minimum_trust=.1,
                      request_config=None) -> basemodels.Manifest:
    model = {
        'requester_restricted_answer_set': {
            '0': {
                'en': 'English Answer 1'
            },
            '1': {
                'en': 'English Answer 2',
                'answer_example_uri': 'https://hcaptcha.com/example_answer2.jpg'
            }
        },
        'request_type': request_type,
        'requester_accuracy_target': minimum_trust,
        'requester_question': {
            "en": "How much money are we to make"
        },
        'requester_question_example': FAKE_URL,
    }

    if request_config:
        model.update({'request_config': request_config})

    manifest = basemodels.NestedManifest(model)
    manifest.validate()

    return manifest


class ManifestTest(unittest.TestCase):
    """Manifest specific tests, validating that models work the way we want"""

    def test_basic_construction(self):
        """Tests that manifest can validate the test manifest properly."""
        a_manifest()

    def test_can_fail_toconstruct(self):
        """Tests that the manifest raises an Error when called with falsy parameters."""
        a_manifest(-1)
        self.assertRaises(schematics.exceptions.DataError, a_manifest, "invalid amount")

    def test_can_fail_toconstruct2(self):
        """Tests that validated fields can't be broken without an exception."""
        mani = a_manifest()
        mani.taskdata_uri = 'test'
        self.assertRaises(schematics.exceptions.DataError, mani.validate)

    def test_can_make_request_config_job(self):
        """Test that jobs with valid request_config parameter work"""
        manifest = a_manifest(
            request_type='image_label_area_select', request_config={'shape_type': 'point'})

    def test_can_make_nested_request_config_job_single_nest(self):
        """Test that jobs with valid nested request_config parameter work"""
        nested_manifest = a_nested_manifest(
            request_type='image_label_area_select', request_config={'shape_type': 'point'})

        manifest = a_manifest(
            request_type='multi_challenge', multi_challenge_manifests=[nested_manifest])

    def test_can_make_nested_request_config_job_multiple_nest(self):
        """Test that jobs with multiple valid nested request_config parameters work"""
        nested_manifest = a_nested_manifest(
            request_type='image_label_area_select', request_config={'shape_type': 'point'})

        nested_manifest_2 = a_nested_manifest(
            request_type='image_label_area_select', request_config={'shape_type': 'point'})

        manifest = a_manifest(
            request_type='multi_challenge',
            multi_challenge_manifests=[nested_manifest, nested_manifest_2])

    def test_can_bad_request_config(self):
        """Test that an invalid shape_type in request_config will fail"""
        manifest = a_manifest()
        manifest.request_type = 'image_label_area_select'
        manifest.request_config = {'shape_type': 'not-a-real-option'}
        self.assertRaises(schematics.exceptions.DataError, manifest.validate)

    def test_gets_default_restrictedanswerset(self):
        """Make sure that the image_label_area_select jobs get a default RAS"""
        model = {
            'job_mode': 'batch',
            'request_type': 'image_label_area_select',
            'unsafe_content': False,
            'task_bid_price': 1,
            'oracle_stake': 0.1,
            'expiration_date': 0,
            'minimum_trust_server': .1,
            'minimum_trust_client': .1,
            'requester_accuracy_target': .1,
            'recording_oracle_addr': REC_ORACLE,
            'reputation_oracle_addr': REP_ORACLE,
            'reputation_agent_addr': REP_ORACLE,
            'instant_result_delivery_webhook': CALLBACK_URL,
            'requester_question': {
                "en": "How much money are we to make"
            },
            'requester_question_example': FAKE_URL,
            'job_total_tasks': 5,
            'taskdata_uri': FAKE_URL
        }
        manifest = basemodels.Manifest(model)

        manifest.validate()
        self.assertGreater(len(manifest['requester_restricted_answer_set'].keys()), 0)

    def test_confcalc_configuration_id(self):
        """ Test that key is in manifest """
        manifest = a_manifest()
        manifest.confcalc_configuration_id = 'test_conf_id'
        manifest.validate()

        self.assertTrue("confcalc_configuration_id" in manifest.to_primitive())

    def test_url_or_list_for_example(self):
        """ validates that we can supply a list or a url to example key if ILB """
        model = a_manifest()

        model.requester_question_example = "https://test.com"
        self.assertTrue(model.validate() is None)
        self.assertIsInstance(model.to_primitive()['requester_question_example'], str)

        model.requester_question_example = ["https://test.com"]
        self.assertTrue(model.validate() is None)
        self.assertIsInstance(model.to_primitive()['requester_question_example'], list)

        model.requester_question_example = "non-url"
        self.assertRaises(schematics.exceptions.DataError, model.validate)
        model.requester_question_example = ["non-url"]
        self.assertRaises(schematics.exceptions.DataError, model.validate)

        # dont allow lists in non-ilb types
        model.request_type = "image_label_area_select"
        self.assertRaises(schematics.exceptions.DataError, model.validate)

    def test_restricted_audience(self):
        """ Test that restricted audience is in the Manifest """
        manifest = a_manifest()
        manifest.restricted_audience = {
            "lang": [{
                "en-us": {
                    "score": 0.9
                }
            }],
            "confidence": [{
                "minimum_client_confidence": {
                    "score": 0.9
                }
            }]
        }
        manifest.validate()
        self.assertTrue("restricted_audience" in manifest.to_primitive())
        self.assertTrue("minimum_client_confidence" in manifest.to_primitive()
                        ["restricted_audience"]["confidence"][0])
        self.assertEqual(
            0.9,
            manifest.to_primitive()["restricted_audience"]["confidence"][0]
            ["minimum_client_confidence"]["score"])
        self.assertTrue("en-us" in manifest.to_primitive()["restricted_audience"]["lang"][0])
        self.assertEqual(
            0.9,
            manifest.to_primitive()["restricted_audience"]["lang"][0]["en-us"]["score"])

    def test_realistic_multi_challenge_example(self):
        """ validates a realistic multi_challenge manifest """
        obj = {
            'job_mode': 'batch',
            'request_type': 'image_label_area_select',
            'unsafe_content': False,
            'task_bid_price': 1,
            'oracle_stake': 0.1,
            'expiration_date': 0,
            'minimum_trust_server': .1,
            'minimum_trust_client': .1,
            'requester_accuracy_target': .1,
            'recording_oracle_addr': REC_ORACLE,
            'reputation_oracle_addr': REP_ORACLE,
            'reputation_agent_addr': REP_ORACLE,
            "job_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
            "request_type": "multi_challenge",
            "requester_question": {
                "en": "Please draw a bow around the text shown, select the best corresponding labels, and enter the word depicted by the image."
            },
            "multi_challenge_manifests": [{
                "request_type": "image_label_area_select",
                "job_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
                "requester_question": {
                    "en": "Please draw a bow around the text shown."
                },
                "request_config": {
                    "shape_type": "polygon",
                    "min_points": 1,
                    "max_points": 4,
                    "min_shapes_per_image": 1,
                    "max_shapes_per_image": 4
                }
            },
                                          {
                                              "request_type": "image_label_multiple_choice",
                                              "job_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
                                              "requester_question": {
                                                  "en": "Select the corresponding label."
                                              },
                                              "requester_restricted_answer_set": {
                                                  "print": {
                                                      "en": "Print"
                                                  },
                                                  "hand-writing": {
                                                      "en": "Hand Writing"
                                                  }
                                              },
                                              "request_config": {
                                                  "multiple_choice_max_choices": 1
                                              }
                                          },
                                          {
                                              "request_type": "image_label_multiple_choice",
                                              "job_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
                                              "requester_question": {
                                                  "en": "Select the corresponding labels."
                                              },
                                              "requester_restricted_answer_set": {
                                                  "top-bottom": {
                                                      "en": "Top to Bottom"
                                                  },
                                                  "bottom-top": {
                                                      "en": "Bottom to Top"
                                                  },
                                                  "left-right": {
                                                      "en": "Left to Right"
                                                  },
                                                  "right-left": {
                                                      "en": "Right to Left"
                                                  }
                                              },
                                              "request_config": {
                                                  "multiple_choice_max_choices": 1
                                              }
                                          },
                                          {
                                              "request_type": "image_label_text",
                                              "job_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
                                              "requester_question": {
                                                  "en": "Please enter the word in the image."
                                              }
                                          }],
            "taskdata": [{
                "datapoint_hash": "sha1:5daf66c6031df7f8913bfa0b52e53e3bcd42aab3",
                "datapoint_uri": "http://test.com/task.jpg",
                "task_key": "2279daef-d10a-4b0f-85d1-0ccbf7c8906b"
            }]
        }

        model = basemodels.Manifest(obj)
        # print(model.to_primitive())
        self.assertTrue(model.validate() is None)

    def test_webhook(self):
        """ Test that webhook is correct """
        webhook = {
            "webhook_id": "c26c2e6a-41ab-4218-b39e-6314b760c45c",
            "chunk_completed": [],
            "job_completed": ["http://test.com"]
        }

        model = basemodels.Webhook(webhook)
        model.validate()

        self.assertTrue("webhook_id" in model.to_primitive())

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("urllib3").setLevel(logging.INFO)
    unittest.main()
