from __future__ import absolute_import, annotations

from datetime import datetime

from django.test import TestCase
from wenet.model.user.common import Date, Gender
from wenet.model.user.profile import WeNetUserProfile

from common.rules import MappingRule, DateRule, NumberRule
from ws.models.survey import NumberAnswer, DateAnswer, SingleChoiceAnswer, SurveyAnswer


class TestMappingRule(TestCase):

    def test_working_rule(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": "unwanted_result"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01")
            }
        )
        mapping_rule = MappingRule("Code0", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertEqual("expected_result", user_profile.gender)

    def test_with_missing_question_code(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": "unwanted_result"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code02")
            }
        )
        mapping_rule = MappingRule("Code0", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.gender)

    def test_with_missing_answer_code(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": "unwanted_result"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code03")
            }
        )
        mapping_rule = MappingRule("Code1", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.gender)

    def test_with_different_user_code(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": "unwanted_result"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01")
            }
        )
        mapping_rule = MappingRule("Code1", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("350")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.gender)

    def test_float_rule(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": 0.567
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code02")
            }
        )
        mapping_rule = MappingRule("Code0", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertNotEqual("expected_result", user_profile.gender)
        self.assertEqual(0.567, user_profile.gender)

    def test_integer_rule(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01")
            }
        )
        mapping_rule = MappingRule("Code0", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertNotEqual(1, user_profile.gender)
        self.assertEqual("expected_result", user_profile.gender)

    def test_gender_rule(self):
        answer_mapping = {
            "Code01": "expected_result",
            "Code02": 1,
            "Code03": Gender.MALE
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code03")
            }
        )
        mapping_rule = MappingRule("Code0", answer_mapping, "gender")
        user_profile = WeNetUserProfile.empty("35")
        mapping_rule.apply(user_profile, survey_answer)
        self.assertNotEqual(1, user_profile.gender)
        self.assertEqual(Gender.MALE, user_profile.gender)


class TestDateRule(TestCase):

    def test_working_rule(self):
        right_answer_type = Date(year=1990, month=10, day=2)
        wrong_answer_type = datetime(1990, 10, 2)
        wrong_answer_type_str = "wrong_answer"
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer_type, user_profile.date_of_birth)
        self.assertNotEqual(wrong_answer_type, user_profile.date_of_birth)
        self.assertNotEqual(wrong_answer_type_str, user_profile.date_of_birth)

    def test_with_missing_question_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code1", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(Date(None, None, None), user_profile.date_of_birth)

    def test_with_different_user_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("350")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(Date(None, None, None), user_profile.date_of_birth)

    def test_float_rule(self):
        right_answer_type = Date(year=1990, month=10, day=2)
        wrong_answer_type = 0.567
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer_type, user_profile.date_of_birth)
        self.assertNotEqual(wrong_answer_type, user_profile.date_of_birth)

    def test_integer_rule(self):
        right_answer_type = Date(year=1990, month=10, day=2)
        wrong_answer_type = 123
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer_type, user_profile.date_of_birth)
        self.assertNotEqual(wrong_answer_type, user_profile.date_of_birth)

    def test_gender_rule(self):
        right_answer_type = Date(year=1990, month=10, day=2)
        wrong_answer_type = "wrong_answer"
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer_type, user_profile.date_of_birth)
        self.assertNotEqual(wrong_answer_type, user_profile.date_of_birth)

class TestNumberRule(TestCase):

    def test_working_rule(self):
        right_answer_number = 1
        wrong_answer_number = 2
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer_number, user_profile.creation_ts)
        self.assertNotEqual(wrong_answer_number, user_profile.creation_ts)

    def test_with_missing_question_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code1", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.creation_ts)

    def test_with_different_user_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("350")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.creation_ts)

    def test_float_rule(self):
        right_answer = 1
        wrong_answer = 2.345
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer, user_profile.creation_ts)
        self.assertNotEqual(wrong_answer, user_profile.creation_ts)

    def test_string_rule(self):
        right_answer = 1
        wrong_answer = "wrong_answer"
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer, user_profile.creation_ts)
        self.assertNotEqual(wrong_answer, user_profile.creation_ts)

    def test_gender_rule(self):
        right_answer = 1
        wrong_answer = Gender.MALE
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(right_answer, user_profile.creation_ts)
        self.assertNotEqual(wrong_answer, user_profile.creation_ts)