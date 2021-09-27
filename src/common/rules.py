from __future__ import absolute_import, annotations

import logging
from abc import abstractmethod, ABC
from datetime import date
from numbers import Number
from typing import List, Dict, Any

from wenet.model.user.common import Date
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


class LanguageRule(Rule):

    def __init__(self, question_code: str, question_mapping: Dict[str, str], answer_mapping: Dict[str, Number]):
        self.question_code = question_code
        self.question_mapping = question_mapping
        self.answer_mapping = answer_mapping

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer) and self.question_code in survey_answer.answers:
            language_list = survey_answer.answers[self.question_code].answer
            #logging.info(f"clicked language list: {language_list}")
            for language_code in language_list:
                if language_code in survey_answer.answers:
                    language_score_code = survey_answer.answers[language_code].answer
                    if language_code in self.question_mapping:
                        question_variable = self.question_mapping[language_code]
                        if language_score_code in self.answer_mapping:
                            answer_number = self.answer_mapping[language_score_code]
                            competence_value = {"name": question_variable, "ontology": "language proficiency", "level": answer_number}
                            user_profile.competences.append(competence_value)
                            #logging.info(f"updated competence with: {competence_value}")
                            #logging.info(f"language: {language_code} levels chosen: {language_score_code}")
                        else:
                            logging.warning(f"{language_score_code} is not in the score mapping")
                    else:
                        logging.warning(f"{language_code} is not in the language mapping")
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile



class CompetenceRule(Rule):

    def __init__(self, variable_name: str, answer_value: Number):
        self.variable_name = variable_name
        self.answer_value = answer_value

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if isinstance(self.variable_name, str) and isinstance(self.answer_value, Number):
                competence_value = {"name": self.variable_name, "ontology": None, "level": self.answer_value}
                user_profile.competences.append(competence_value)
                logging.info(f"updated competence with {user_profile.competences}")
        else:
            logging.warning(f"Trying to apply rule to not matching user_id: {user_profile.profile_id}, survey_id: {survey_answer.wenet_id}")
        return user_profile

