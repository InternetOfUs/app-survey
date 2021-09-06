from __future__ import absolute_import, annotations

import logging
from abc import abstractmethod, ABC
from datetime import date
from typing import List, Dict

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


class BirtDateRule(Rule):

    def __init__(self, question_code: str) -> None:
        self.question_code = question_code

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.question_code in survey_answer.answers:
            answer_date = survey_answer.answers[self.question_code].answer
            if isinstance(answer_date, date):
                user_profile.date_of_birth = Date(year=answer_date.year, month=answer_date.month, day=answer_date.day)
        return user_profile


class GenderRule(Rule):

    def __init__(self, question_code: str, answer_mapping: Dict[str, Gender]) -> None:
        self.question_code = question_code
        self.answer_mapping = answer_mapping

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.question_code in survey_answer.answers:
            user_profile.gender = self.answer_mapping[survey_answer.answers[self.question_code].answer] if survey_answer.answers[self.question_code].answer else user_profile.gender
        return user_profile
