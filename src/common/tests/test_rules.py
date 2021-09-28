from __future__ import absolute_import, annotations

from datetime import datetime

from django.test import TestCase
from wenet.model.user.common import Date, Gender
from wenet.model.user.profile import WeNetUserProfile

from common.rules import MappingRule, DateRule, NumberRule, LanguageRule
from ws.models.survey import NumberAnswer, DateAnswer, SingleChoiceAnswer, SurveyAnswer, MultipleChoicesAnswer


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


class TestLanguageRule(TestCase):

    def test_working_rule(self):
        question_mapping = {
            "CodeL1": "expected_language",
            "CodeL2": "expected_language",
            "CodeL3": "unwanted_language"
        }

        answer_mapping = {
            "CodeA1": 1,
            "CodeA2": 1,
            "CodeA3": 0
        }
        expected_value = {"name": "expected_language", "ontology": "language proficiency", "level": 1}
        expected_value_list = [expected_value]

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL1", "CodeL2"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1"),
                "CodeL3": SingleChoiceAnswer("CodeL3", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1")
            }
        )
        language_rule = LanguageRule("CodeLQ", question_mapping, answer_mapping)
        user_profile = WeNetUserProfile.empty("35")
        language_rule.apply(user_profile, survey_answer)
        self.assertIn(expected_value, user_profile.competences)
        self.assertListEqual(expected_value_list, user_profile.competences)


    def test_with_missing_language_code(self):
        question_mapping = {
            "CodeL1": "expected_language",
            "CodeL2": "unwanted_language"
        }

        answer_mapping = {
            "CodeA1": 0,
            "CodeA2": 0.5,
            "CodeA3": 1
        }
        expected_value = {"name": "expected_language", "ontology": "language proficiency", "level": 1}
        expected_value_list = [expected_value]

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL3"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1")
            }
        )
        language_rule = LanguageRule("CodeLQ", question_mapping, answer_mapping)
        user_profile = WeNetUserProfile.empty("35")
        language_rule.apply(user_profile, survey_answer)
        self.assertNotIn(expected_value, user_profile.competences)
        self.assertListEqual([], user_profile.competences)


    def test_with_missing_score_code(self):
        question_mapping = {
            "CodeL1": "expected_language",
            "CodeL2": "expected_language",
            "CodeL3": "unwanted_language"
        }

        answer_mapping = {
            "CodeA1": 1,
            "CodeA2": 2,
            "CodeA3": 3
        }
        expected_value = {"name": "expected_language", "ontology": "language proficiency", "level": 1}
        expected_value_list = [expected_value]

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL1"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA4")
            }
        )
        language_rule = LanguageRule("CodeLQ", question_mapping, answer_mapping)
        user_profile = WeNetUserProfile.empty("35")
        language_rule.apply(user_profile, survey_answer)
        self.assertNotIn(expected_value, user_profile.competences)
        self.assertListEqual([], user_profile.competences)


    def test_with_different_user_code(self):
        question_mapping = {
            "CodeL1": "expected_language",
            "CodeL2": "expected_language",
            "CodeL3": "unwanted_language"
        }

        answer_mapping = {
            "CodeA1": 0,
            "CodeA2": 1,
            "CodeA3": 2
        }
        expected_value = {"name": "expected_language", "ontology": "language proficiency", "level": 1}
        expected_value_list = [expected_value]

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL1", "CodeL2"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1"),
                "CodeL3": SingleChoiceAnswer("CodeL3", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1")
            }
        )
        language_rule = LanguageRule("CodeLQ", question_mapping, answer_mapping)
        user_profile = WeNetUserProfile.empty("350")
        language_rule.apply(user_profile, survey_answer)
        self.assertNotIn(expected_value, user_profile.competences)
        self.assertListEqual([], user_profile.competences)