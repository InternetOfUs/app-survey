from __future__ import absolute_import, annotations

from unittest.mock import Mock

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.tasks import CeleryTask


class TestSurveyEventView(APITestCase):

    def test_post(self):
        CeleryTask.update_user_profile = Mock(return_value=None)
        url = f"/{settings.BASE_URL}survey/event/"
        response = self.client.post(
            url,
            {
                "eventId": "4f1e64b6-8745-45d0-b123-f0cafe5ea365",
                "eventType": "FORM_RESPONSE",
                "createdAt": "2021-08-24T11:20:11.081Z",
                "data": {
                    "responseId": "d9c4d2fc-3eec-4c9e-afa4-0afa2503b590",
                    "respondentId": "n9BX25",
                    "formId": "mR01vw",
                    "formName": "Test WeNet survey\n",
                    "createdAt": "2021-08-24T11:20:10.000Z",
                    "fields": [{
                        "key": "question_wgb0RD_5cce3ba2-31a7-4237-84cb-2b6c6daf708f",
                        "label": "wenetId",
                        "type": "HIDDEN_FIELDS",
                        "value": "1"
                    }, {
                        "key": "question_wkbYPJ",
                        "label": "A01: Which gender were you born?",
                        "type": "MULTIPLE_CHOICE",
                        "value": "a2f049cd-0b22-4ca9-a6fc-0f85abb34fef",
                        "options": [{
                            "id": "a2f049cd-0b22-4ca9-a6fc-0f85abb34fef",
                            "text": "1: Male"
                        }, {
                            "id": "372b4749-0350-44ae-9154-de29f796ece6",
                            "text": "2: Female"
                        }, {
                            "id": "4d5cb12a-3395-425b-9365-5b52d9578ff3",
                            "text": "3: Other"
                        }, {
                            "id": "c1331187-094d-4e63-8ad3-ec3149a3008a",
                            "text": "4: Non-Binary"
                        }, {
                            "id": "d9700222-4a40-4b93-bb2b-2438fcb01b35",
                            "text": "5: Not-Say"
                        }]
                    }, {
                        "key": "question_3yXDG6",
                        "label": "A02: When were you born?",
                        "type": "INPUT_DATE",
                        "value": "1998-10-18"
                    }, {
                        "key": "question_wLD0NJ",
                        "label": "D04: How many informal study groups do you participate in?",
                        "type": "INPUT_NUMBER",
                        "value": 4
                    }, {
                        "key": "question_wAz4PD",
                        "label": None,
                        "type": "CHECKBOXES",
                        "value": [
                            "5c96b263-f3de-4392-b1b3-f3ef043f80ed"
                        ],
                        "options": [
                            {
                                "id": "5c96b263-f3de-4392-b1b3-f3ef043f80ed",
                                "text": "I authorize the WeNet project members to access my university's administrative data."
                            }
                        ]
                    }]
                }
            },
            format="json"
        )
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        CeleryTask.update_user_profile.assert_called_once()

    def test_post_no_payload(self):
        CeleryTask.update_user_profile = Mock(return_value=None)
        url = f"/{settings.BASE_URL}survey/event/"
        response = self.client.post(url)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        CeleryTask.update_user_profile.assert_not_called()

    def test_post_wrong_payload(self):
        CeleryTask.update_user_profile = Mock(return_value=None)
        url = f"/{settings.BASE_URL}survey/event/"
        response = self.client.post(
            url,
            {
                "eventId": "4f1e64b6-8745-45d0-b123-f0cafe5ea365",
                "eventType": "FORM_RESPONSE",
                "createdAt": "2021-08-24T11:20:11.081Z",
                "data": {
                    "responseId": "d9c4d2fc-3eec-4c9e-afa4-0afa2503b590",
                    "respondentId": "n9BX25",
                    "formId": "mR01vw",
                    "formName": "Test WeNet survey\n",
                    "createdAt": "2021-08-24T11:20:10.000Z"
                }
            },
            format="json"
        )
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        CeleryTask.update_user_profile.assert_not_called()
