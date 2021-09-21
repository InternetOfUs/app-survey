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
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile


class MappingRule(Rule):

    def __init__(self, question_code: str, answer_mapping: Dict[str, Any], profile_attribute: str) -> None:
        self.question_code = question_code
        self.answer_mapping = answer_mapping
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            if survey_answer.answers[self.question_code].answer in self.answer_mapping:
                mapping_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
                setattr(user_profile, self.profile_attribute, mapping_result)
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile


class NumberRule(Rule):

    def __init__(self, question_code: str, profile_attribute: str) -> None:
        self.question_code = question_code
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            answer_number = survey_answer.answers[self.question_code].answer
            if isinstance(answer_number, Number):
                setattr(user_profile, self.profile_attribute, answer_number)
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile


class CompetenceEntryRule(Rule):

    def __init__(self, question_mapping: Dict[str, str], question_code: str, answer_value: Number):
        self.question_mapping = question_mapping
        self.question_code = question_code
        self.answer_value = answer_value

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            answer_number = survey_answer.answers[self.question_code].answer
            if isinstance(answer_number, Number):
                #add Dict[variable, value, null?] combo to a competence field of a user_profile
                competence_value = {"name": "English", "level": 0.5}
                user_profile.competences.append(competence_value)
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile
