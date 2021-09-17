from __future__ import absolute_import, annotations

from datetime import datetime

from django.test import TestCase
from wenet.model.user.common import Date
from wenet.model.user.profile import WeNetUserProfile

from common.rules import MappingRule, DateRule, NumberingRule
from ws.models.survey import NumberAnswer, DateAnswer, SingleChoiceAnswer, SurveyAnswer


class TestMappingRule(TestCase):

    def test_rule(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": "unwanted_result"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            # code0: question code
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01")
            }
        )
        # test it with int, float, string, with different types
        mappingrule = MappingRule("Code0", answer_mapping, "gender")
        userprofile = WeNetUserProfile.empty("35")
        mappingrule.apply(userprofile, survey_answer)
        self.assertEqual("expected_result", userprofile.gender)


class TestDateRule(TestCase):

    def test_rule(self):
        right_answer_type = Date(year=1990, month=10, day=2)
        wrong_answer_type = datetime(1990, 10, 2)

        survey_answer = SurveyAnswer(
            wenet_id="35",
            # code0: question code
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        daterule = DateRule("Code0", "date_of_birth")
        userprofile = WeNetUserProfile.empty("35")
        daterule.apply(userprofile, survey_answer)
        self.assertEqual(right_answer_type, userprofile.date_of_birth)
        self.assertNotEqual(wrong_answer_type, userprofile.date_of_birth)


class TestNumberingRule(TestCase):

    def test_rule(self):
        right_answer_number = 1
        wrong_answer_number = 2
        survey_answer = SurveyAnswer(
            wenet_id="35",
            # code0: question code
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        numberrule = NumberingRule("Code0", "creation_ts")
        userprofile = WeNetUserProfile.empty("35")
        numberrule.apply(userprofile, survey_answer)
        self.assertEqual(right_answer_number, userprofile.creation_ts)
        self.assertNotEqual(wrong_answer_number, userprofile.creation_ts)
