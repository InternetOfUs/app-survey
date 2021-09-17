from __future__ import absolute_import, annotations

import logging
from abc import abstractmethod, ABC
from datetime import date
from numbers import Number
from typing import List, Dict, Any

from wenet.model.user.common import Gender, Date
from wenet.model.user.profile import WeNetUserProfile

from ws.models.survey import SurveyAnswer

logger = logging.getLogger("wenet-survey-web-app.common.profile")


class RuleManager:

    def __init__(self, rules: List[Rule]) -> None:
        self.rules = rules

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def update_user_profile(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        for rule in self.rules:
            user_profile = rule.apply(user_profile, survey_answer)
        return user_profile


class Rule(ABC):

    @abstractmethod
    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        pass

    @staticmethod
    def check_wenet_id(user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> bool:
        return user_profile.profile_id == survey_answer.wenet_id


class DateRule(Rule):

    def __init__(self, question_code: str, profile_attribute: str) -> None:
        self.question_code = question_code
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            answer_date = survey_answer.answers[self.question_code].answer
            if isinstance(answer_date, date):
                date_result = Date(year=answer_date.year, month=answer_date.month, day=answer_date.day)
                setattr(user_profile, self.profile_attribute, date_result)
        return user_profile


class MappingRule(Rule):

    def __init__(self, question_code: str, answer_mapping: Dict[str, Any], profile_attribute: str) -> None:
        self.question_code = question_code
        self.answer_mapping = answer_mapping
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            mapping_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
            setattr(user_profile, self.profile_attribute, mapping_result)
        return user_profile


class NumberingRule(Rule):

    def __init__(self, question_code: str, profile_attribute: str) -> None:
        self.question_code = question_code
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            answer_number = survey_answer.answers[self.question_code].answer
            if isinstance(answer_number, Number):
                setattr(user_profile, self.profile_attribute, answer_number)
        return user_profile
