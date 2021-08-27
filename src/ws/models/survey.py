from __future__ import absolute_import, annotations

import logging
import re
from abc import abstractmethod
from dataclasses import dataclass
from datetime import date
from numbers import Number
from typing import List, Any, Optional, Dict

from ws.models.tally import FormField, SurveyData, LinearScaleField, RatingField, DropdownField, NumberField, DateField, \
    MultipleChoiceField, CheckboxesField, CheckboxesFieldValue

logger = logging.getLogger("wenet-survey-web-app.ws.models.survey")


class AnswerBuilder:

    @staticmethod
    def build(raw_answer: dict) -> Optional[Answer]:
        answer_type = raw_answer.get("type")
        if answer_type == NumberAnswer.FIELD_TYPE:
            return NumberAnswer.from_repr(raw_answer)
        elif answer_type == DateAnswer.FIELD_TYPE:
            return DateAnswer.from_repr(raw_answer)
        elif answer_type == SingleChoiceAnswer.FIELD_TYPE:
            return SingleChoiceAnswer.from_repr(raw_answer)
        elif answer_type == MultipleChoicesAnswer.FIELD_TYPE:
            return MultipleChoicesAnswer.from_repr(raw_answer)
        else:
            logger.warning(f"Unrecognized type of Answer [{answer_type}]")
            return None

    @staticmethod
    def from_tally(field: FormField) -> Optional[Answer]:
        question_code = AnswerBuilder._get_question_code_from_tally(field.question)
        if field.field_type in [NumberField.FIELD_TYPE, LinearScaleField.FIELD_TYPE, RatingField.FIELD_TYPE]:
            if question_code is not None and field.answer is not None:
                return NumberAnswer(
                    question=question_code,
                    field_type=NumberAnswer.FIELD_TYPE,
                    answer=field.answer
                )
            else:
                return None
        elif field.field_type == DateField.FIELD_TYPE:
            if question_code is not None and field.answer is not None:
                return DateAnswer(
                    question=question_code,
                    field_type=DateAnswer.FIELD_TYPE,
                    answer=field.answer
                )
            else:
                return None
        elif field.field_type in [MultipleChoiceField.FIELD_TYPE, DropdownField.FIELD_TYPE]:
            answer_code = AnswerBuilder._get_answer_code_from_tally(field.answer) if field.answer else None
            if question_code is not None and answer_code is not None:
                return SingleChoiceAnswer(
                    question=question_code,
                    field_type=SingleChoiceAnswer.FIELD_TYPE,
                    answer=answer_code
                )
            else:
                return None
        elif field.field_type == CheckboxesField.FIELD_TYPE:
            answer_code = [AnswerBuilder._get_answer_code_from_tally(answer) for answer in field.answer] if field.answer else None
            if question_code is not None and answer_code is not None:
                return MultipleChoicesAnswer(
                    question=question_code,
                    field_type=MultipleChoicesAnswer.FIELD_TYPE,
                    answer=answer_code
                )
            else:
                return None
        elif field.field_type == CheckboxesFieldValue.FIELD_TYPE:
            return None
        else:
            logger.warning(f"Unrecognized type of FormField [{field.field_type}]")
            return None

    @staticmethod
    def _get_question_code_from_tally(question: str) -> Optional[str]:
        match = re.match(r"([A-Za-z01-9]+): (.+)", question)  # TODO define where to to insert the code of the question
        if match:
            return match.group(1)
        else:
            logger.warning(f"Not a valid format for a question [{question}]")
            return None

    @staticmethod
    def _get_answer_code_from_tally(answer: str) -> Optional[str]:
        match = re.match(r"([A-Za-z01-9]+): (.+)", answer)  # TODO define where to to insert the code of the answer (same as question?)
        if match:
            return match.group(1)
        else:
            logger.warning(f"Not a valid format for an answer [{answer}]")
            return None


@dataclass
class Answer:

    question: str
    field_type: str
    answer: Any

    def to_repr(self) -> dict:
        return {
            "question": self.question,
            "type": self.field_type,
            "answer": self.answer
        }

    @staticmethod
    @abstractmethod
    def from_repr(raw_answer: dict) -> Answer:
        pass


@dataclass
class NumberAnswer(Answer):

    FIELD_TYPE = "NUMBER"
    answer: Optional[Number]

    @staticmethod
    def from_repr(raw_answer: dict) -> NumberAnswer:
        return NumberAnswer(
            question=raw_answer["question"],
            field_type=raw_answer["type"],
            answer=raw_answer["answer"]
        )


@dataclass
class DateAnswer(Answer):

    FIELD_TYPE = "DATE"
    answer: Optional[date]

    def to_repr(self) -> dict:
        return {
            "question": self.question,
            "type": self.field_type,
            "answer": self.answer.isoformat() if self.answer else self.answer
        }

    @staticmethod
    def from_repr(raw_answer: dict) -> DateAnswer:
        return DateAnswer(
            question=raw_answer["question"],
            field_type=raw_answer["type"],
            answer=date.fromisoformat(raw_answer["answer"])
        )


@dataclass
class SingleChoiceAnswer(Answer):

    FIELD_TYPE = "SINGLE_CHOICE"
    answer: Optional[str]

    @staticmethod
    def from_repr(raw_answer: dict) -> SingleChoiceAnswer:
        return SingleChoiceAnswer(
            question=raw_answer["question"],
            field_type=raw_answer["type"],
            answer=raw_answer["answer"]
        )


@dataclass
class MultipleChoicesAnswer(Answer):

    FIELD_TYPE = "MULTIPLE_CHOICES"
    answer: Optional[List[str]]  # list with the ids of the selected options

    @staticmethod
    def from_repr(raw_answer: dict) -> MultipleChoicesAnswer:
        return MultipleChoicesAnswer(
            question=raw_answer["question"],
            field_type=raw_answer["type"],
            answer=raw_answer["answer"]
        )


@dataclass
class SurveyAnswer:

    wenet_id: str
    answers: Dict[str, Answer]  # dict with the key the question and value the Answer

    def to_repr(self) -> dict:
        return {
            "wenetId": self.wenet_id,
            "answers": [self.answers[key].to_repr() for key in self.answers]
        }

    @staticmethod
    def from_repr(raw_survey_answer: dict) -> SurveyAnswer:
        answers = [AnswerBuilder.build(raw_answer) for raw_answer in raw_survey_answer["answers"]]
        return SurveyAnswer(
            wenet_id=raw_survey_answer["wenetId"],
            answers={answer.question: answer for answer in answers if answer}
        )

    @staticmethod
    def from_tally(survey: SurveyData) -> SurveyAnswer:
        answers = [AnswerBuilder.from_tally(answer) for answer in survey.answers]
        return SurveyAnswer(
            wenet_id=survey.wenet_id,
            answers={answer.question: answer for answer in answers if answer}
        )
