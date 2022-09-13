from __future__ import absolute_import, annotations

from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time
from wenet.model.user.common import Date, Gender
from wenet.model.user.profile import WeNetUserProfile

from common.enumerator import AnswerOrder
from common.rules import MappingRule, DateRule, NumberRule, LanguageRule, \
    CompetenceMeaningNumberRule, CompetenceMeaningMappingRule, MaterialsMappingRule, MaterialsFieldRule, \
    CompetenceMeaningBuilderRule, NumberToDateRule, UniversityMappingRule
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
            "Code01": "unwanted_result",
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
        self.assertNotEqual("unwanted_result", user_profile.gender)
        self.assertEqual(0.567, user_profile.gender)

    def test_integer_rule(self):
        answer_mapping = {
            "Code01": "unwanted_result",
            "Code02": 1
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
        self.assertNotEqual("unwanted_result", user_profile.gender)
        self.assertEqual(1, user_profile.gender)

    def test_gender_rule(self):
        answer_mapping = {
            "Code01": "unwanted_result",
            "Code02": Gender.MALE
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
        self.assertNotEqual("unwanted_result", user_profile.gender)
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
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=0.567)
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(Date(None, None, None), user_profile.date_of_birth)

    def test_integer_rule(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=123)
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(Date(None, None, None), user_profile.date_of_birth)

    def test_single_choice_answer(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        date_rule = DateRule("Code0", "date_of_birth")
        user_profile = WeNetUserProfile.empty("35")
        date_rule.apply(user_profile, survey_answer)
        self.assertEqual(Date(None, None, None), user_profile.date_of_birth)


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

    def test_date_answer(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.creation_ts)

    def test_single_choice_answer(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        number_rule = NumberRule("Code0", "creation_ts")
        user_profile = WeNetUserProfile.empty("35")
        number_rule.apply(user_profile, survey_answer)
        self.assertEqual(None, user_profile.creation_ts)


class TestLanguageRule(TestCase):

    def test_working_rule(self):
        # create new lang entry on the first run, enrich it, update the first entry on the second run
        question_mapping = {
            "CodeL1": "l1",
            "CodeL2": "l2",
            "CodeL3": "l3"
        }
        answer_mapping = {
            "CodeA1": 0,
            "CodeA2": 0.5,
            "CodeA3": 1
        }
        competences_answer1 = {"name": "l1", "ontology": "language", "level": 0}
        competences_answer2 = {"name": "l2", "ontology": "language", "level": 0.5}
        competences_answer3 = {"name": "l3", "ontology": "language", "level": 1}
        edited_competences_answer = {"name": "l1", "ontology": "language", "level": 0.5}
        competences_answer = [edited_competences_answer, competences_answer2, competences_answer3]

        survey_answer_add = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL1", "CodeL2"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1"),
                "CodeL3": SingleChoiceAnswer("CodeL3", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA1")
            }
        )
        survey_answer_edit = SurveyAnswer(
            wenet_id="35",
            answers={
                "CodeLQ": MultipleChoicesAnswer("CodeLQ", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["CodeL1"]),
                "CodeL1": SingleChoiceAnswer("CodeL1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="CodeA2")
            }
        )
        language_rule = LanguageRule("CodeLQ", question_mapping, answer_mapping)
        user_profile = WeNetUserProfile.empty("35")
        language_rule.apply(user_profile, survey_answer_add)
        self.assertIn(competences_answer1, user_profile.competences)
        self.assertListEqual([competences_answer1], user_profile.competences)

        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        language_rule.apply(user_profile, survey_answer_edit)
        self.assertIn(edited_competences_answer, user_profile.competences)
        self.assertEqual(competences_answer, user_profile.competences)

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
        expected_value = {"name": "expected_language", "ontology": "language", "level": 1}

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
        expected_value = {"name": "expected_language", "ontology": "language", "level": 1}

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
        expected_value = {"name": "expected_language", "ontology": "language", "level": 1}

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


class TestCompetenceMeaningNumberRule(TestCase):

    def test_working_rule(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        expected_competences_answer = {"name": "n1", "ontology": "o1", "level": 1}
        competences_answer = [expected_competences_answer, competences_answer2, competences_answer3]
        expected_meanings_answer = {"name": "expected_meanings_value", "category": "test_category", "level": 1}
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=6),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=6)
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "n1", ceiling_value, "o1", "competences")
        test_meanings_rule = CompetenceMeaningNumberRule("Code1", "expected_meanings_value", ceiling_value, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertIn(expected_competences_answer, user_profile.competences)
        self.assertEqual(competences_answer, user_profile.competences)
        self.assertIn(expected_meanings_answer, user_profile.meanings)
        self.assertEqual([expected_meanings_answer], user_profile.meanings)

    def test_working_rule_ontology_none(self):
        competences_answer1 = {"name": "n1", "ontology": None, "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": None, "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        expected_competences_answer = {"name": "n1", "ontology": None, "level": 1}
        competences_answer = [expected_competences_answer, competences_answer2, competences_answer3]
        expected_meanings_answer = {"name": "expected_meanings_value", "category": "test_category", "level": 1}
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=6),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=6)
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "n1", ceiling_value, None, "competences")
        test_meanings_rule = CompetenceMeaningNumberRule("Code1", "expected_meanings_value", ceiling_value, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertIn(expected_competences_answer, user_profile.competences)
        self.assertEqual(competences_answer, user_profile.competences)
        self.assertIn(expected_meanings_answer, user_profile.meanings)
        self.assertEqual([expected_meanings_answer], user_profile.meanings)

    def test_with_missing_question_code(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=6)
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code1", "expected_competences_value", ceiling_value, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_wrong_profile_entry(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=6)
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "expected_competences_value", ceiling_value, "test_category", "wrong_field")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_date_type(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "expected_competences_value", ceiling_value, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_single_choice_type(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "expected_competences_value", ceiling_value, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_multiple_choice_type(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["01", "02"])
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "expected_competences_value", ceiling_value, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_different_user_code(self):
        ceiling_value = 6

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=6)
            }
        )
        test_competences_rule = CompetenceMeaningNumberRule("Code0", "expected_competences_value", ceiling_value, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("3500")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)


class TestCompetenceMeaningMappingRule(TestCase):

    def test_working_rule(self):
        # expected_competences_answer should replace the first entry of the competences
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        expected_competences_answer = {"name": "n1", "ontology": "o1", "level": 0}
        competences_answer = [expected_competences_answer, competences_answer2, competences_answer3]
        expected_meanings_answer = {"name": "expected_meanings_value", "category": "test_category", "level": 1}
        score_mapping = {
            "01": 0,
            "02": 1
        }

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="02")
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "n1", score_mapping, "o1", "competences")
        test_meanings_rule = CompetenceMeaningMappingRule("Code1", "expected_meanings_value", score_mapping, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertEqual(competences_answer, user_profile.competences)
        self.assertIn(expected_competences_answer, user_profile.competences)
        self.assertIn(expected_meanings_answer, user_profile.meanings)
        self.assertEqual([expected_meanings_answer], user_profile.meanings)

    def test_with_number_type(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_multiple_choice_type(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["01", "02"])
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_date_type(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_missing_mapping_entry(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="03")
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code1", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_missing_question_code(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code1", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_wrong_profile_entry(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "expected_competences_value", score_mapping, "test_category", "wrong_field")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_different_user_code(self):
        score_mapping = {
            "01": 0,
            "02": 1
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_competences_rule = CompetenceMeaningMappingRule("Code0", "expected_competences_value", score_mapping, "test_category", "competences")
        user_profile = WeNetUserProfile.empty("3500")
        test_competences_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)


class TestMaterialsFieldRule(TestCase):

    def test_working_rule(self):
        materials_answer1 = {"name": "n1", "classification": "c1", "description": 1, "quantity": 1}
        materials_answer2 = {"name": "n2", "classification": "c1", "description": 2, "quantity": 1}
        materials_answer = [materials_answer1, materials_answer2]
        survey_answer_create = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        survey_answer_add = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=2)
            }
        )
        materials_rule1 = MaterialsFieldRule("Code0", "n1", "c1")
        materials_rule2 = MaterialsFieldRule("Code0", "n2", "c1")
        user_profile = WeNetUserProfile.empty("35")
        materials_rule1.apply(user_profile, survey_answer_create)
        self.assertIn(materials_answer1, user_profile.materials)
        self.assertEqual([materials_answer1], user_profile.materials)

        materials_rule2.apply(user_profile, survey_answer_add)
        self.assertIn(materials_answer2, user_profile.materials)
        self.assertEqual(materials_answer, user_profile.materials)

    def test_with_date_type(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        test_materials_rule = MaterialsFieldRule("Code0", "expected_materials_value", "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_single_choice_type(self):
        answer = "01"
        expected_materials_answer = {"name": "expected_materials_value", "classification": "test_classification",
                                     "description": answer, "quantity": 1}

        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_materials_rule = MaterialsFieldRule("Code0", "expected_materials_value", "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertIn(expected_materials_answer, user_profile.materials)

    def test_with_multiple_choice_type(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["01", "02"])
            }
        )
        test_materials_rule = MaterialsFieldRule("Code0", "expected_materials_value", "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_wrong_parameter_type(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_materials_rule = MaterialsFieldRule("Code0", "expected_materials_value", 123)
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_missing_question_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_materials_rule = MaterialsFieldRule("Code1", "expected_materials_value", "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_different_user_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_materials_rule = MaterialsFieldRule("Code0", "expected_materials_value", "test_classification")
        user_profile = WeNetUserProfile.empty("3500")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)


class TestMaterialsMappingRule(TestCase):

    def test_working_rule(self):
        materials_answer1 = {"name": "n1", "classification": "c1", "description": "expected_answer1", "quantity": 1}
        materials_answer2 = {"name": "n2", "classification": "c1", "description": "expected_answer2", "quantity": 1}
        materials_answer = [materials_answer1, materials_answer2]

        existing_material = {"name": "n1", "classification": "c1", "description": "old_answer", "quantity": 1}

        test_mapping = {
            "01": "expected_answer1",
            "02": "expected_answer2"
        }
        survey_answer_create = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        survey_answer_add = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="02")
            }
        )
        materials_rule1 = MaterialsMappingRule("Code0", "n1", test_mapping, "c1")
        materials_rule2 = MaterialsMappingRule("Code0", "n2", test_mapping, "c1")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.materials = [
            existing_material
        ]
        materials_rule1.apply(user_profile, survey_answer_create)
        self.assertIn(materials_answer1, user_profile.materials)
        self.assertEqual([materials_answer1], user_profile.materials)

        materials_rule2.apply(user_profile, survey_answer_add)
        self.assertIn(materials_answer2, user_profile.materials)
        self.assertEqual(materials_answer, user_profile.materials)

    def test_working_rule_no_ontology(self):
        materials_answer1 = {"name": "n1", "classification": None, "description": "expected_answer1", "quantity": 1}
        materials_answer2 = {"name": "n2", "classification": None, "description": "expected_answer2", "quantity": 1}
        materials_answer = [materials_answer1, materials_answer2]
        test_mapping = {
            "01": "expected_answer1",
            "02": "expected_answer2"
        }
        survey_answer_create = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        survey_answer_add = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="02")
            }
        )
        materials_rule1 = MaterialsMappingRule("Code0", "n1", test_mapping, None)
        materials_rule2 = MaterialsMappingRule("Code0", "n2", test_mapping, None)
        user_profile = WeNetUserProfile.empty("35")
        user_profile.materials = [
            {"name": "n1", "classification": None, "description": "old answer", "quantity": 1}
        ]
        materials_rule1.apply(user_profile, survey_answer_create)
        self.assertIn(materials_answer1, user_profile.materials)
        self.assertEqual([materials_answer1], user_profile.materials)

        materials_rule2.apply(user_profile, survey_answer_add)
        self.assertIn(materials_answer2, user_profile.materials)
        self.assertEqual(materials_answer, user_profile.materials)

    def test_with_date_type(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_number_type(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_multiple_choice_type(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["01", "02"])
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_missing_mapping_entry(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="03")
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_wrong_parameter_type(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", 123, test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_missing_question_code(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_materials_rule = MaterialsMappingRule("Code1", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_different_user_code(self):
        test_mapping = {
            "01": "expected_answer",
            "02": "unexpected_answer"
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01")
            }
        )
        test_materials_rule = MaterialsMappingRule("Code0", "expected_materials_value", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("40000")
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)


class TestCompetenceMeaningBuilderRule(TestCase):

    def test_working_rule(self):
        # (normal 5 + normal 5 + normal 5 + normal 5) divided by 4 divided by 5 = 1
        # expected_competences_answer should replace the 1st entry of the list
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        expected_competences_answer = {"name": "n1", "ontology": "o1", "level": 1}
        competences_answer = [expected_competences_answer, competences_answer2, competences_answer3]
        expected_meanings_answer = {"name": "n1", "category": "c1", "level": 1}
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.NORMAL,
            "Code2": AnswerOrder.NORMAL,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code2": NumberAnswer("Code2", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code3": NumberAnswer("Code3", field_type=NumberAnswer.FIELD_TYPE, answer=5),
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "n1", 5, "o1", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "n1", 5, "c1", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertEqual(competences_answer, user_profile.competences)
        self.assertIn(expected_competences_answer, user_profile.competences)
        self.assertIn(expected_meanings_answer, user_profile.meanings)
        self.assertEqual([expected_meanings_answer], user_profile.meanings)

    def test_none_selected(self):
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.NORMAL,
            "Code2": AnswerOrder.NORMAL,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code4": NumberAnswer("Code4", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code5": NumberAnswer("Code5", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code6": NumberAnswer("Code6", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code7": NumberAnswer("Code7", field_type=NumberAnswer.FIELD_TYPE, answer=5),
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_single_choice_type(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3]
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code2": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="5"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="5"),
                "Code2": SingleChoiceAnswer("Code2", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="5"),
                "Code3": SingleChoiceAnswer("Code3", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="5")
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertListEqual(competences_answer, user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_multiple_choice_type(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3]
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code2": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["5", "6"]),
                "Code1": MultipleChoicesAnswer("Code1", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["5", "6"]),
                "Code2": MultipleChoicesAnswer("Code2", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["5", "6"]),
                "Code3": MultipleChoicesAnswer("Code3", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["5", "6"])
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertListEqual(competences_answer, user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_date_type(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3]
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code2": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2)),
                "Code1": DateAnswer("Code1", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2)),
                "Code2": DateAnswer("Code2", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2)),
                "Code3": DateAnswer("Code3", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 2))
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertListEqual(competences_answer, user_profile.competences)
        self.assertListEqual([], user_profile.meanings)

    def test_with_missing_mapping_question(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        expected_competences_answer = {"name": "test_competences_value", "ontology": "test_ontology", "level": 0.467}
        expected_meanings_answer = {"name": "test_meanings_value", "category": "test_category", "level": 0.467}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3, expected_competences_answer]
        # (normal 5 + reverse 5 + reverse 5) divided by 3 divided by 5 = 0.467
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL,
            "Code2": AnswerOrder.REVERSE
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code2": NumberAnswer("Code2", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code4": NumberAnswer("Code4", field_type=NumberAnswer.FIELD_TYPE, answer=5)
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertEqual(competences_answer, user_profile.competences)
        self.assertIn(expected_competences_answer, user_profile.competences)
        self.assertIn(expected_meanings_answer, user_profile.meanings)
        self.assertEqual([expected_meanings_answer], user_profile.meanings)

    def test_with_wrong_profile_entry(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3]
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code2": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code2": NumberAnswer("Code2", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code3": NumberAnswer("Code3", field_type=NumberAnswer.FIELD_TYPE, answer=5)
            }
        )
        test_competencies_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competencies")
        test_materials_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "materials")
        user_profile = WeNetUserProfile.empty("35")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competencies_rule.apply(user_profile, survey_answer)
        test_materials_rule.apply(user_profile, survey_answer)
        self.assertListEqual(competences_answer, user_profile.competences)
        self.assertListEqual([], user_profile.meanings)
        self.assertListEqual([], user_profile.materials)

    def test_with_different_user_code(self):
        competences_answer1 = {"name": "n1", "ontology": "o1", "level": 0.1}
        competences_answer2 = {"name": "n2", "ontology": "o1", "level": 0.2}
        competences_answer3 = {"name": "n3", "ontology": "o2", "level": 0.3}
        competences_answer = [competences_answer1, competences_answer2, competences_answer3]
        order_mapping = {
            "Code0": AnswerOrder.NORMAL,
            "Code1": AnswerOrder.REVERSE,
            "Code2": AnswerOrder.REVERSE,
            "Code3": AnswerOrder.NORMAL
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code2": NumberAnswer("Code2", field_type=NumberAnswer.FIELD_TYPE, answer=5),
                "Code3": NumberAnswer("Code3", field_type=NumberAnswer.FIELD_TYPE, answer=5)
            }
        )
        test_competences_rule = CompetenceMeaningBuilderRule(order_mapping, "test_competences_value", 5, "test_ontology", "competences")
        test_meanings_rule = CompetenceMeaningBuilderRule(order_mapping, "test_meanings_value", 5, "test_category", "meanings")
        user_profile = WeNetUserProfile.empty("3000")
        user_profile.competences.append(competences_answer1)
        user_profile.competences.append(competences_answer2)
        user_profile.competences.append(competences_answer3)
        test_competences_rule.apply(user_profile, survey_answer)
        test_meanings_rule.apply(user_profile, survey_answer)
        self.assertListEqual(competences_answer, user_profile.competences)
        self.assertListEqual([], user_profile.meanings)


class TestNumberToDateRule(TestCase):

    def test_working_rule(self):
        # update the year of birth according to the number field age entry
        # if birthdate doesn't exist, update the date as january 1st
        existing_birthdate = Date(year=1999, month=10, day=2)
        updated_birthdate = Date(year=2000, month=10, day=2)
        created_birthdate = Date(year=2000, month=1, day=1)
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=21)
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile_existing = WeNetUserProfile.empty("35")
            user_profile_existing.date_of_birth = existing_birthdate
            numtodate_rule.apply(user_profile_existing, survey_answer)
            self.assertEqual(updated_birthdate, user_profile_existing.date_of_birth)

            user_profile_created = WeNetUserProfile.empty("35")
            numtodate_rule.apply(user_profile_created, survey_answer)
            self.assertEqual(created_birthdate, user_profile_created.date_of_birth)

    def test_working_rule_with_profile_with_empty_birthdate(self):
        created_birthdate = Date(year=2000, month=1, day=1)
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=21)
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile_existing = WeNetUserProfile.empty("35")
            user_profile_existing.date_of_birth = None
            numtodate_rule.apply(user_profile_existing, survey_answer)
            self.assertEqual(created_birthdate, user_profile_existing.date_of_birth)

    def test_with_missing_question_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code1", "date_of_birth")
            user_profile = WeNetUserProfile.empty("35")
            numtodate_rule.apply(user_profile, survey_answer)
            self.assertEqual((Date(None, None, None)), user_profile.date_of_birth)

    def test_date_type(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": DateAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer=datetime(2000, 1, 1))
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile = WeNetUserProfile.empty("35")
            numtodate_rule.apply(user_profile, survey_answer)
            self.assertEqual((Date(None, None, None)), user_profile.date_of_birth)

    def test_single_choice_answer(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=DateAnswer.FIELD_TYPE, answer="some_date")
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile = WeNetUserProfile.empty("35")
            numtodate_rule.apply(user_profile, survey_answer)
            self.assertEqual((Date(None, None, None)), user_profile.date_of_birth)

    def test_multiple_choice_answer(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": MultipleChoicesAnswer("Code0", field_type=MultipleChoicesAnswer.FIELD_TYPE, answer=["date1", "date2"])
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile = WeNetUserProfile.empty("35")
            numtodate_rule.apply(user_profile, survey_answer)
            self.assertEqual((Date(None, None, None)), user_profile.date_of_birth)

    def test_with_different_user_code(self):
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": NumberAnswer("Code0", field_type=NumberAnswer.FIELD_TYPE, answer=21)
            }
        )
        with freeze_time("2021-07-31"):
            numtodate_rule = NumberToDateRule("Code0", "date_of_birth")
            user_profile = WeNetUserProfile.empty("3000")
            numtodate_rule.apply(user_profile, survey_answer)
            self.assertEqual((Date(None, None, None)), user_profile.date_of_birth)


class TestUniversityMappingRule(TestCase):

    def test_working_rule(self):
        department_degree_answer_init = {
            "name": "test_department_or_degree",
            "classification": "test_classification",
            "description": "u1_test_department_degree1",
            "quantity": 1
        }
        department_degree_answer_edit = {
            "name": "test_department_or_degree",
            "classification": "test_classification",
            "description": "u1_test_department_degree2",
            "quantity": 1
        }

        univ1_department_degree_mapping = {
            "U1D1": "u1_test_department_degree1",
            "U1D2": "u1_test_department_degree2"
        }
        univ2_department_degree_mapping = {
            "U2D1": "u2_test_department_degree1",
            "U2D2": "u2_test_department_degree2"
        }
        department_degree_mapping = {
            "01": univ1_department_degree_mapping,
            "02": univ2_department_degree_mapping
        }
        survey_answer_init = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D1")
            }
        )
        survey_answer_edit = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D2")
            }
        )
        univ_rule1 = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", department_degree_mapping, "test_classification")
        univ_rule2 = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", department_degree_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")

        univ_rule1.apply(user_profile, survey_answer_init)
        self.assertIn(department_degree_answer_init, user_profile.materials)
        self.assertEqual([department_degree_answer_init], user_profile.materials)

        univ_rule2.apply(user_profile, survey_answer_edit)
        self.assertIn(department_degree_answer_edit, user_profile.materials)
        self.assertEqual([department_degree_answer_edit], user_profile.materials)

    def test_with_date_type(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
                },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
                }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": DateAnswer("Code1", field_type=DateAnswer.FIELD_TYPE, answer=datetime(1990, 10, 3))
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_number_type(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=1)
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_multiple_choice_type(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": MultipleChoicesAnswer("Code1", field_type=DateAnswer.FIELD_TYPE, answer=["U1D1", "U1D1"])
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_missing_mapping_entry(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="03"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D1")
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_wrong_parameter_type(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D1")
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", 123, test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_missing_question_code(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code2": SingleChoiceAnswer("Code2", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D1")
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)

    def test_with_different_user_code(self):
        test_mapping = {
            "01": {
                "U1D1": "u1_test_department_degree1",
                "U1D2": "u1_test_department_degree2"
            },
            "02": {
                "U2D1": "u2_test_department_degree1",
                "U2D2": "u2_test_department_degree2"
            }
        }
        survey_answer = SurveyAnswer(
            wenet_id="35",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="U1D1")
            }
        )
        test_university_rule = UniversityMappingRule("Code0", "Code1", "test_department_or_degree", test_mapping, "test_classification")
        user_profile = WeNetUserProfile.empty("35000")
        test_university_rule.apply(user_profile, survey_answer)
        self.assertListEqual([], user_profile.materials)
