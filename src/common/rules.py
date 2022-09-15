from __future__ import absolute_import, annotations

import logging
from abc import abstractmethod, ABC
from datetime import date
from datetime import datetime
from numbers import Number
from typing import List, Dict, Any, Optional

from wenet.model.user.common import Date
from wenet.model.user.profile import WeNetUserProfile

from common.enumerator import AnswerOrder
from ws.models.survey import SurveyAnswer

logger = logging.getLogger("wenet-survey-web-app.common.profile")


class RuleManager:

    def __init__(self, rules: List[Rule]) -> None:
        self.rules = rules

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def update_user_profile(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        for rule in self.rules:
            try:
                user_profile = rule.apply(user_profile, survey_answer)
            except Exception as e:
                logger.exception(f"An error occurred while executing a {type(rule)}", exc_info=e)
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
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                answer_date = survey_answer.answers[self.question_code].answer
                if isinstance(answer_date, date):
                    date_result = Date(year=answer_date.year, month=answer_date.month, day=answer_date.day)
                    setattr(user_profile, self.profile_attribute, date_result)
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class NumberToDateRule(Rule):

    def __init__(self, question_code: str, profile_attribute: str) -> None:
        self.question_code = question_code
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                answer_number = survey_answer.answers[self.question_code].answer
                if isinstance(answer_number, int):
                    this_year = datetime.now().year
                    date_year = this_year - answer_number
                    date_month = 1
                    date_day = 1
                    if getattr(user_profile, self.profile_attribute) is not None and isinstance(getattr(user_profile, self.profile_attribute), Date):
                        if getattr(user_profile, self.profile_attribute).month is not None:
                            date_month = getattr(user_profile, self.profile_attribute).month
                        if getattr(user_profile, self.profile_attribute).day is not None:
                            date_day = getattr(user_profile, self.profile_attribute).day
                    date_result = Date(year=date_year, month=date_month, day=date_day)
                    setattr(user_profile, self.profile_attribute, date_result)
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class MappingRule(Rule):

    def __init__(self, question_code: str, answer_mapping: Dict[str, Any], profile_attribute: str) -> None:
        self.question_code = question_code
        self.answer_mapping = answer_mapping
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if survey_answer.answers[self.question_code].answer in self.answer_mapping:
                    mapping_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
                    setattr(user_profile, self.profile_attribute, mapping_result)
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class NumberRule(Rule):

    def __init__(self, question_code: str, profile_attribute: str) -> None:
        self.question_code = question_code
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                answer_number = survey_answer.answers[self.question_code].answer
                if isinstance(answer_number, Number):
                    setattr(user_profile, self.profile_attribute, answer_number)
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class LanguageRule(Rule):

    def __init__(self, question_code: str, question_mapping: Dict[str, str], answer_mapping: Dict[str, Number]):
        self.question_code = question_code
        self.question_mapping = question_mapping
        self.answer_mapping = answer_mapping

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                language_list = survey_answer.answers[self.question_code].answer
                for language_code in language_list:
                    if language_code in survey_answer.answers:
                        language_score_code = survey_answer.answers[language_code].answer
                        if language_code in self.question_mapping:
                            question_variable = self.question_mapping[language_code]
                            if language_score_code in self.answer_mapping:
                                answer_number = self.answer_mapping[language_score_code]
                                competence_value = {"name": question_variable, "ontology": "language", "level": answer_number}
                                add_to_profile = True
                                for competence in user_profile.competences:
                                    if competence.get("ontology", "") == "language" and competence.get("name", "") == question_variable:
                                        competence["level"] = answer_number
                                        add_to_profile = False
                                        break
                                if add_to_profile:
                                    user_profile.competences.append(competence_value)
                                    logger.debug(f"updated competence with: {competence_value}")
                            else:
                                logger.warning(f"{language_score_code} is not in the score mapping")
                        else:
                            logger.warning(f"{language_code} is not in the language mapping")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class CompetenceMeaningNumberRule(Rule):

    def __init__(self, question_code: str, variable_name: str, ceiling_value: int, category_name: Optional[str],
                 profile_attribute: str, floor_value: int = 1):
        self.question_code = question_code
        self.variable_name = variable_name
        self.category_name = category_name
        self.profile_attribute = profile_attribute
        self.ceiling_value = ceiling_value
        self.floor_value = floor_value

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.variable_name, str) \
                        and isinstance(survey_answer.answers[self.question_code].answer, int):
                    if self.ceiling_value > 1:
                        answer_number = survey_answer.answers[self.question_code].answer
                        answer_percent = (answer_number - self.floor_value) / (self.ceiling_value - self.floor_value)  # line that transforms number into float percentage
                        profile_entry = None
                        add_to_profile = True
                        if self.profile_attribute == "meanings":
                            profile_entry = {"name": self.variable_name, "category": self.category_name, "level": answer_percent}
                            for meaning in user_profile.meanings:
                                if meaning.get("category", "") == self.category_name and meaning.get("name", "") == self.variable_name:
                                    meaning["level"] = answer_percent
                                    add_to_profile = False
                                    break
                        elif self.profile_attribute == "competences":
                            profile_entry = {"name": self.variable_name, "ontology": self.category_name, "level": answer_percent}
                            for competence in user_profile.competences:
                                if competence.get("ontology", "") == self.category_name and competence.get("name", "") == self.variable_name:
                                    competence["level"] = answer_percent
                                    add_to_profile = False
                                    break
                        else:
                            logger.warning(f"{self.profile_attribute} field is not supported in the user profile")
                        if profile_entry is not None and add_to_profile:
                            getattr(user_profile, self.profile_attribute).append(profile_entry)
                            logger.debug(f"updated {self.profile_attribute} with {getattr(user_profile, self.profile_attribute)}")
                    else:
                        logger.debug(f"ceiling value is too low to build {self.variable_name} attribute of the user {user_profile.profile_id}")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class CompetenceMeaningMappingRule(Rule):

    def __init__(self, question_code: str, variable_name: str, answer_mapping: Dict[str, Number], category_name: str,
                 profile_attribute: str):
        self.question_code = question_code
        self.variable_name = variable_name
        self.answer_mapping = answer_mapping
        self.category_name = category_name
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.category_name, str) and isinstance(self.variable_name, str) \
                        and not isinstance(survey_answer.answers[self.question_code].answer, list) and survey_answer.answers[self.question_code].answer in self.answer_mapping:
                    mapping_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
                    profile_entry = None
                    add_to_profile = True
                    if self.profile_attribute == "meanings":
                        profile_entry = {"name": self.variable_name, "category": self.category_name, "level": mapping_result}
                        for meaning in user_profile.meanings:
                            if meaning.get("category", "") == self.category_name and meaning.get("name", "") == self.variable_name:
                                meaning["level"] = mapping_result
                                add_to_profile = False
                                break
                    elif self.profile_attribute == "competences":
                        profile_entry = {"name": self.variable_name, "ontology": self.category_name, "level": mapping_result}
                        for competence in user_profile.competences:
                            if competence.get("ontology", "") == self.category_name and competence.get("name", "") == self.variable_name:
                                competence["level"] = mapping_result
                                add_to_profile = False
                                break
                    else:
                        logger.warning(f"{self.profile_attribute} field is not supported in the user profile")
                    if profile_entry is not None and add_to_profile:
                        getattr(user_profile, self.profile_attribute).append(profile_entry)
                        logger.debug(f"updated {self.profile_attribute} with {getattr(user_profile, self.profile_attribute)}")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class MaterialsMappingRule(Rule):

    def __init__(self, question_code: str, variable_name: str, answer_mapping: Dict[str, str], classification: Optional[str]):
        self.question_code = question_code
        self.variable_name = variable_name
        self.answer_mapping = answer_mapping
        self.classification = classification

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.variable_name, str) and not isinstance(survey_answer.answers[self.question_code].answer, list) and survey_answer.answers[self.question_code].answer in self.answer_mapping:
                    mapping_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
                    profile_entry = {"name": self.variable_name, "classification": self.classification, "description": mapping_result, "quantity": 1}
                    add_to_profile = True
                    for material in user_profile.materials:
                        if material.get("classification", "") == self.classification and material.get("name", "") == self.variable_name:
                            material["description"] = mapping_result
                            add_to_profile = False
                            break
                    if add_to_profile:
                        user_profile.materials.append(profile_entry)
                        logger.debug(f"updated materials with: {profile_entry}")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class MaterialsFieldRule(Rule):

    def __init__(self, question_code: str, variable_name: str, classification: str):
        self.question_code = question_code
        self.variable_name = variable_name
        self.classification = classification

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.classification, str) and isinstance(self.variable_name, str):
                    if isinstance(survey_answer.answers[self.question_code].answer, str) or isinstance(survey_answer.answers[self.question_code].answer, int):
                        answer = survey_answer.answers[self.question_code].answer
                        profile_entry = {"name": self.variable_name, "classification": self.classification, "description": answer, "quantity": 1}
                        add_to_profile = True
                        for material in user_profile.materials:
                            if material.get("classification", "") == self.classification and material.get("name", "") == self.variable_name:
                                material["description"] = answer
                                add_to_profile = False
                                break
                        if add_to_profile:
                            user_profile.materials.append(profile_entry)
                            logger.debug(f"updated materials with: {profile_entry}")
                    else:
                        logger.warning(f"field type {type(survey_answer.answers[self.question_code].answer)} is not supported")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class MaterialsQuantityRule(Rule):

    def __init__(self, question_code: str, variable_name: str, classification: Optional[str], description: Optional[str] = None):
        self.question_code = question_code
        self.variable_name = variable_name
        self.classification = classification
        self.description = description

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.variable_name, str):
                    if isinstance(survey_answer.answers[self.question_code].answer, int):
                        answer = survey_answer.answers[self.question_code].answer
                        profile_entry = {"name": self.variable_name, "classification": self.classification, "description": self.description, "quantity": answer}
                        add_to_profile = True
                        for material in user_profile.materials:
                            if material.get("classification", "") == self.classification and material.get("name", "") == self.variable_name:
                                material["description"] = self.description
                                material["quantity"] = answer
                                add_to_profile = False
                                break
                        if add_to_profile:
                            user_profile.materials.append(profile_entry)
                            logger.debug(f"updated materials with: {profile_entry}")
                    else:
                        logger.warning(f"field type {type(survey_answer.answers[self.question_code].answer)} is not supported")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class CompetenceMeaningBuilderRule(Rule):

    def __init__(self, order_mapping: Dict[str, AnswerOrder], variable_name: str, ceiling_value: int,
                 category_name: str, profile_attribute: str):
        self.order_mapping = order_mapping
        self.variable_name = variable_name
        self.ceiling_value = ceiling_value
        self.category_name = category_name
        self.profile_attribute = profile_attribute

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            selected_question_codes_str = all(isinstance(question_code, str) for question_code in self.order_mapping.keys())
            selected_answers_int = []
            for question_code in self.order_mapping.keys():
                if question_code in survey_answer.answers:
                    selected_answers_int.append(isinstance(survey_answer.answers[question_code].answer, int))

            if selected_question_codes_str and all(selected_answers_int) and isinstance(self.variable_name, str) and isinstance(self.category_name, str) and isinstance(self.ceiling_value, int) and isinstance(self.profile_attribute, str):
                required_answers = []
                for question_code in self.order_mapping.keys():
                    if question_code in survey_answer.answers:
                        answer_number = survey_answer.answers[question_code].answer
                        if self.order_mapping.get(question_code) == AnswerOrder.REVERSE:
                            answer_number = (self.ceiling_value + 1) - answer_number
                        required_answers.append(answer_number)
                # ((A1+A2+A3+A4)/4/)5 or ((A1+A2+A3)/3)/5 in case of equation changes, see this line
                if required_answers:
                    if self.ceiling_value > 0:
                        number_value = round((sum(required_answers) / len(required_answers)) / self.ceiling_value, 3)
                        profile_entry = None
                        add_to_profile = True
                        if self.profile_attribute == "meanings":
                            profile_entry = {"name": self.variable_name, "category": self.category_name, "level": number_value}
                            for meaning in user_profile.meanings:
                                if meaning.get("category", "") == self.category_name and meaning.get("name", "") == self.variable_name:
                                    meaning["level"] = number_value
                                    add_to_profile = False
                                    break
                        elif self.profile_attribute == "competences":
                            profile_entry = {"name": self.variable_name, "ontology": self.category_name, "level": number_value}
                            for competence in user_profile.competences:
                                if competence.get("ontology", "") == self.category_name and competence.get("name", "") == self.variable_name:
                                    competence["level"] = number_value
                                    add_to_profile = False
                                    break
                        else:
                            logger.warning(f"{self.profile_attribute} field is not supported in the user profile")
                        if profile_entry is not None and add_to_profile:
                            getattr(user_profile, self.profile_attribute).append(profile_entry)
                            logger.debug(f"updated {self.profile_attribute} with {getattr(user_profile, self.profile_attribute)}")
                    else:
                        logger.debug(f"ceiling value is too low to build {self.variable_name} attribute of the user {user_profile.profile_id}")
                else:
                    logger.debug(f"No answer is selected to build {self.variable_name} attribute of the user {user_profile.profile_id}")
        else:
            logger.warning(
                f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class UniversityMappingRule(Rule):

    def __init__(self, question_code: str, field_code: str, variable_name: str, answer_mapping: Dict[str, Dict[str, str]], classification: str):
        self.question_code = question_code
        self.field_code = field_code
        self.variable_name = variable_name
        self.answer_mapping = answer_mapping
        self.classification = classification

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers and self.field_code in survey_answer.answers:
                univ_exists = survey_answer.answers[self.question_code].answer in self.answer_mapping
                field_exists = survey_answer.answers[self.field_code].answer
                code_not_list = not isinstance(survey_answer.answers[self.question_code].answer, list)
                field_not_list = not isinstance(survey_answer.answers[self.field_code].answer, list)
                if isinstance(self.question_code, str) and isinstance(self.field_code, str) and isinstance(self.classification, str) and isinstance(self.variable_name, str) \
                        and code_not_list and field_not_list and univ_exists and field_exists:
                    univ_result = self.answer_mapping[survey_answer.answers[self.question_code].answer]
                    if survey_answer.answers[self.field_code].answer in univ_result.keys():
                        univ_code = survey_answer.answers[self.field_code].answer
                        selected_answer = univ_result[univ_code]
                        profile_entry = {"name": self.variable_name, "classification": self.classification, "description": selected_answer, "quantity": 1}
                        add_to_profile = True
                        for material in user_profile.materials:
                            if material.get("classification", "") == self.classification and material.get("name", "") == self.variable_name:
                                material["description"] = selected_answer
                                add_to_profile = False
                                break
                        if add_to_profile:
                            user_profile.materials.append(profile_entry)
                            logger.debug(f"updated materials with: {profile_entry}")
                    else:
                        logger.debug(f"{self.variable_name} not selected for the user {user_profile.profile_id}")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


class UniversityFromDepartmentRule(Rule):

    def __init__(self, question_code: str, variable_name: str, classification: str):
        self.question_code = question_code
        self.variable_name = variable_name
        self.classification = classification

    @staticmethod
    def _get_university_from_department_code(department_response: str) -> str:
        if department_response.startswith("NUM"):
            return "NUM"
        elif department_response.startswith("LSE"):
            return "LSE"
        elif department_response.startswith("AAU"):
            return "AAU"
        elif department_response.startswith("UNITN"):
            return "UNITN"
        elif department_response.startswith("UC"):
            return "UC"
        else:
            raise ValueError(f"Unable to retrieve an university from department code [{department_response}]")

    def apply(self, user_profile: WeNetUserProfile, survey_answer: SurveyAnswer) -> WeNetUserProfile:
        if self.check_wenet_id(user_profile, survey_answer):
            if self.question_code in survey_answer.answers:
                if isinstance(self.question_code, str) and isinstance(self.classification, str) and isinstance(self.variable_name, str) \
                        and not isinstance(survey_answer.answers[self.question_code].answer, list):

                    answer_code = survey_answer.answers[self.question_code].answer
                    university = self._get_university_from_department_code(answer_code)

                    profile_entry = {"name": self.variable_name, "classification": self.classification, "description": university, "quantity": 1}
                    add_to_profile = True
                    for material in user_profile.materials:
                        if material.get("classification", "") == self.classification and material.get("name", "") == self.variable_name:
                            material["description"] = university
                            add_to_profile = False
                            break
                    if add_to_profile:
                        user_profile.materials.append(profile_entry)
                        logger.debug(f"updated materials with: {profile_entry}")
            else:
                logger.debug(f"Trying to apply rule but question code [{self.question_code}] is not selected by user")
        else:
            logger.warning(f"Trying to apply rule but the user ID [{user_profile.profile_id}] does not match the user ID in the survey [{survey_answer.wenet_id}]")
        return user_profile


