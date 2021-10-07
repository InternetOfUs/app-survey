from __future__ import absolute_import, annotations

from datetime import date, datetime

from django.test import TestCase

from ws.models.survey import NumberAnswer, DateAnswer, AnswerBuilder, SingleChoiceAnswer, MultipleChoicesAnswer, \
    SurveyAnswer
from ws.models.tally import NumberField, LinearScaleField, RatingField, DateField, MultipleChoiceField, DropdownField, \
    CheckboxesField, HiddenField, SurveyData


class TestAnswerBuilder(TestCase):

    def test_build(self):
        answer = NumberAnswer(
            question="Code",
            field_type=NumberAnswer.FIELD_TYPE,
            answer=1
        )
        self.assertEqual(answer, AnswerBuilder.build(answer.to_repr()))

        answer = DateAnswer(
            question="Code",
            field_type=DateAnswer.FIELD_TYPE,
            answer=date(2020, 2, 3)
        )
        self.assertEqual(answer, AnswerBuilder.build(answer.to_repr()))

        answer = SingleChoiceAnswer(
            question="Code",
            field_type=SingleChoiceAnswer.FIELD_TYPE,
            answer="Code"
        )
        self.assertEqual(answer, AnswerBuilder.build(answer.to_repr()))

        answer = MultipleChoicesAnswer(
            question="Code",
            field_type=MultipleChoicesAnswer.FIELD_TYPE,
            answer=["Code1", "Code2"]
        )
        self.assertEqual(answer, AnswerBuilder.build(answer.to_repr()))

        self.assertIsNone(AnswerBuilder.build({
            "question": "",
            "type": "",
            "answer": ""
        }))

    def test_from_tally(self):
        answer = NumberAnswer(
            question="Code",
            field_type=NumberAnswer.FIELD_TYPE,
            answer=1
        )
        tally_field = NumberField(
            question="Code: Question",
            field_type=NumberField.FIELD_TYPE,
            answer=1
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        tally_field = LinearScaleField(
            question="Code: Question",
            field_type=LinearScaleField.FIELD_TYPE,
            answer=1
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        tally_field = RatingField(
            question="Code: Question",
            field_type=RatingField.FIELD_TYPE,
            answer=1
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        answer = DateAnswer(
            question="Code",
            field_type=DateAnswer.FIELD_TYPE,
            answer=date(2020, 2, 3)
        )
        tally_field = DateField(
            question="Code: Question",
            field_type=DateField.FIELD_TYPE,
            answer=date(2020, 2, 3)
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        answer = SingleChoiceAnswer(
            question="Code",
            field_type=SingleChoiceAnswer.FIELD_TYPE,
            answer="Code"
        )
        tally_field = MultipleChoiceField(
            question="Code: Question",
            field_type=MultipleChoiceField.FIELD_TYPE,
            answer="Code: Answer"
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        tally_field = DropdownField(
            question="Code: Question",
            field_type=DropdownField.FIELD_TYPE,
            answer="Code: Answer"
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        answer = MultipleChoicesAnswer(
            question="Code",
            field_type=MultipleChoicesAnswer.FIELD_TYPE,
            answer=["Code1", "Code2"]
        )
        tally_field = CheckboxesField(
            question="Code: Question",
            field_type=CheckboxesField.FIELD_TYPE,
            answer=["Code1: Answer 1", "Code2: Answer 2"]
        )
        self.assertEqual(answer, AnswerBuilder.from_tally(tally_field))

        self.assertIsNone(AnswerBuilder.from_tally(HiddenField("", HiddenField.FIELD_TYPE, "")))

    def test_get_question_code_from_tally(self):
        self.assertEqual("Code", AnswerBuilder._get_question_code_from_tally("Code: Question"))

        self.assertIsNone(AnswerBuilder._get_question_code_from_tally("Question"))

    def test_get_answer_code_from_tally(self):
        self.assertEqual("Code", AnswerBuilder._get_answer_code_from_tally("Code: Answer"))

        self.assertIsNone(AnswerBuilder._get_answer_code_from_tally("Answer"))


class TestSurveyAnswer(TestCase):

    def test_repr(self):
        survey_answer = SurveyAnswer(
            wenet_id="1",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01"),
                "Code1": SingleChoiceAnswer("Code1", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code13")
            }
        )
        self.assertEqual(survey_answer, SurveyAnswer.from_repr(survey_answer.to_repr()))

    def test_from_tally(self):
        survey_answer = SurveyAnswer(
            wenet_id="1",
            answers={
                "Code0": SingleChoiceAnswer("Code0", field_type=SingleChoiceAnswer.FIELD_TYPE, answer="Code01"),
                "Code1": NumberAnswer("Code1", field_type=NumberAnswer.FIELD_TYPE, answer=3)
            }
        )
        tally_survey_data = SurveyData(
            form_id="formId",
            created_at=datetime.now(),
            wenet_id="1",
            answers=[
                MultipleChoiceField("Code0: Question0", field_type=MultipleChoiceField.FIELD_TYPE, answer="Code01: Answer01"),
                RatingField("Code1: Question1", field_type=RatingField.FIELD_TYPE, answer=3),
                HiddenField("Question2", field_type=HiddenField.FIELD_TYPE, answer="String"),
                CheckboxesField("Question3", field_type=CheckboxesField.FIELD_TYPE, answer=["Choice1", "Choice2"])
            ]
        )
        self.assertEqual(survey_answer, SurveyAnswer.from_tally(tally_survey_data))
