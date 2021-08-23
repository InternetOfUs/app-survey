from __future__ import absolute_import, annotations

from dataclasses import dataclass
from datetime import datetime, date
from numbers import Number
from typing import List, Any


@dataclass
class FormField:

    key: str
    label: str
    field_type: str
    value: Any


@dataclass
class HiddenField(FormField):

    FIELD_TYPE = "HIDDEN_FIELDS"
    value: str


@dataclass
class NumberField(FormField):

    FIELD_TYPE = "INPUT_NUMBER"
    value: Number


@dataclass
class DateField(FormField):

    FIELD_TYPE = "INPUT_DATE"
    value: date


@dataclass
class LinearScaleField(FormField):

    FIELD_TYPE = "LINEAR_SCALE"
    value: int


@dataclass
class RatingField(FormField):

    FIELD_TYPE = "RATING"
    value: int


@dataclass
class MultipleChoiceOption:

    choice_id: str
    text: str


@dataclass
class MultipleChoiceField(FormField):

    FIELD_TYPE = "MULTIPLE_CHOICE"
    value: str
    options: List[MultipleChoiceOption]


@dataclass
class DropdownField(FormField):

    FIELD_TYPE = "DROPDOWN"
    value: str
    options: List[MultipleChoiceOption]


@dataclass
class CheckboxesField(FormField):

    FIELD_TYPE = "CHECKBOXES"
    value: List[str]  # list with the ids of the selected options
    options: List[MultipleChoiceOption]


@dataclass
class SurveyData:

    response_id: str
    respondent_id: str
    form_id: str
    form_name: str
    created_at: datetime
    fields: List[FormField]


@dataclass
class SurveyEvent:

    event_id: str
    event_type: str
    created_at: datetime
    data: SurveyData
