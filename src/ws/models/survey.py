from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import date, datetime
from numbers import Number
from typing import List, Any, Optional, Dict


@dataclass
class FormField:

    question: str
    field_type: str
    answer: Any


@dataclass
class HiddenField(FormField):

    FIELD_TYPE = "HIDDEN_FIELDS"
    answer: Optional[str]


@dataclass
class NumberField(FormField):

    FIELD_TYPE = "INPUT_NUMBER"
    answer: Optional[Number]


@dataclass
class DateField(FormField):

    FIELD_TYPE = "INPUT_DATE"
    answer: Optional[date]


@dataclass
class LinearScaleField(FormField):

    FIELD_TYPE = "LINEAR_SCALE"
    answer: Optional[int]


@dataclass
class RatingField(FormField):

    FIELD_TYPE = "RATING"
    answer: Optional[int]


@dataclass
class MultipleChoiceOption:

    choice_id: str
    text: str


@dataclass
class MultipleChoiceField(FormField):

    FIELD_TYPE = "MULTIPLE_CHOICE"
    answer: Optional[str]


@dataclass
class DropdownField(FormField):

    FIELD_TYPE = "DROPDOWN"
    answer: Optional[str]


@dataclass
class CheckboxesField(FormField):

    FIELD_TYPE = "CHECKBOXES"
    answer: Optional[List[str]]  # list with the ids of the selected options


@dataclass
class SurveyData:

    form_id: str
    created_at: datetime
    wenet_id: str
    answers: Dict[str, FormField]  # dict with the key the question and value the FormField
