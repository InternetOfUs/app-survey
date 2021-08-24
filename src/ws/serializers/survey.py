from __future__ import absolute_import, annotations

import logging
import re

from rest_framework import serializers

from ws.models.survey import SurveyData, FormField, HiddenField, MultipleChoiceOption, NumberField, \
    LinearScaleField, RatingField, MultipleChoiceField, DropdownField, CheckboxesField, DateField


logger = logging.getLogger("wenet-survey-web-app.ws.serializers.survey")


class FormFieldHandler:

    @staticmethod
    def to_repr(form_field: FormField) -> dict:
        if form_field.field_type == HiddenField.FIELD_TYPE:
            serializer = HiddenFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == NumberField.FIELD_TYPE:
            serializer = NumberFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == DateField.FIELD_TYPE:
            serializer = DateFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == LinearScaleField.FIELD_TYPE:
            serializer = LinearScaleFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == RatingField.FIELD_TYPE:
            serializer = RatingFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == MultipleChoiceField.FIELD_TYPE:
            serializer = MultipleChoiceFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == DropdownField.FIELD_TYPE:
            serializer = DropdownFieldSerializer(instance=form_field)
            return serializer.data
        elif form_field.field_type == CheckboxesField.FIELD_TYPE:
            serializer = CheckboxesFieldSerializer(instance=form_field)
            return serializer.data
        else:
            raise ValueError(f"Unrecognized type of form field [{type(form_field)}]")

    @staticmethod
    def build(raw_field: dict) -> FormField:
        if raw_field["type"] == HiddenField.FIELD_TYPE:
            serializer = HiddenFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == NumberField.FIELD_TYPE:
            serializer = NumberFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == DateField.FIELD_TYPE:
            serializer = DateFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == LinearScaleField.FIELD_TYPE:
            serializer = LinearScaleFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == RatingField.FIELD_TYPE:
            serializer = RatingFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == MultipleChoiceField.FIELD_TYPE:
            serializer = MultipleChoiceFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == DropdownField.FIELD_TYPE:
            serializer = DropdownFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        elif raw_field["type"] == CheckboxesField.FIELD_TYPE:
            serializer = CheckboxesFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
            else:
                raise ValueError(serializer.errors)
        else:
            raise ValueError(f"Unrecognized type of form field [{raw_field['type']}]")

    @staticmethod
    def get_question_code(question: str) -> str:
        match = re.match(r"([A-Za-z01-9]+): (.+)", question)  # TODO define where to to insert the code of the question
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Not a valid format for a question [{question}]")

    @staticmethod
    def get_answer_code(answer: str) -> str:
        match = re.match(r"([A-Za-z01-9]+): (.+)", answer)  # TODO define where to to insert the code of the answer (same as question?)
        if match:
            return match.group(1)
        else:
            raise ValueError(f"Not a valid format for an answer [{answer}]")


class FormFieldSerializer(serializers.Serializer):

    label = serializers.CharField(max_length=1024, required=True, source="question")
    type = serializers.CharField(max_length=1024, required=True, source="field_type")

    def create(self, validated_data: dict) -> FormField:
        raise NotImplemented()

    def update(self, multiple_choice_option: FormField, validated_data: dict) -> FormField:
        raise NotImplemented()

    def to_representation(self, instance: FormField) -> dict:
        return {
            "question": instance.question,
            "type": instance.field_type,
            "answer": instance.answer
        }


class HiddenFieldSerializer(FormFieldSerializer):

    value = serializers.CharField(max_length=1024, required=True, source="answer")

    def create(self, validated_data: dict) -> HiddenField:
        return HiddenField(
            question=validated_data["question"],
            field_type=validated_data["field_type"],
            answer=validated_data["answer"]
        )


class NumberFieldSerializer(FormFieldSerializer):

    value = serializers.IntegerField(required=True, allow_null=True, source="answer")

    def create(self, validated_data: dict) -> NumberField:
        return NumberField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=validated_data["answer"]
        )


class DateFieldSerializer(FormFieldSerializer):

    value = serializers.DateField(required=True, allow_null=True, source="answer")

    def create(self, validated_data: dict) -> DateField:
        return DateField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=validated_data["answer"]
        )


class LinearScaleFieldSerializer(FormFieldSerializer):

    value = serializers.IntegerField(required=True, allow_null=True, source="answer")

    def create(self, validated_data: dict) -> LinearScaleField:
        return LinearScaleField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=validated_data["answer"]
        )


class RatingFieldSerializer(FormFieldSerializer):

    value = serializers.IntegerField(required=True, allow_null=True, source="answer")

    def create(self, validated_data: dict) -> RatingField:
        return RatingField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=validated_data["answer"]
        )


class MultipleChoiceOptionSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=1024, required=True, source="choice_id")
    text = serializers.CharField(max_length=1024, required=True)

    def create(self, validated_data: dict) -> MultipleChoiceOption:
        multiple_choice_option = MultipleChoiceOption(
            choice_id=validated_data["choice_id"],
            text=validated_data["text"]
        )
        return multiple_choice_option

    def update(self, multiple_choice_option: MultipleChoiceOption, validated_data: dict) -> MultipleChoiceOption:
        raise NotImplemented()


class MultipleChoiceFieldSerializer(FormFieldSerializer):

    value = serializers.CharField(max_length=1024, required=True, allow_null=True, source="answer")
    options = serializers.ListField(required=True)

    def create(self, validated_data: dict) -> MultipleChoiceField:
        answer = None
        for option in validated_data["options"]:
            multiple_choice_option_serializer = MultipleChoiceOptionSerializer(data=option)
            option = multiple_choice_option_serializer.save() if multiple_choice_option_serializer.is_valid() else None
            if option and option.choice_id == validated_data["answer"]:
                answer = option.text

        return MultipleChoiceField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=FormFieldHandler.get_answer_code(answer) if answer else None
        )


class DropdownFieldSerializer(FormFieldSerializer):

    value = serializers.CharField(max_length=1024, required=True, allow_null=True, source="answer")
    options = serializers.ListField(required=True)

    def create(self, validated_data: dict) -> DropdownField:
        answer = None
        for option in validated_data["options"]:
            multiple_choice_option_serializer = MultipleChoiceOptionSerializer(data=option)
            option = multiple_choice_option_serializer.save() if multiple_choice_option_serializer.is_valid() else None
            if option and option.choice_id == validated_data["answer"]:
                answer = option.text

        return DropdownField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=FormFieldHandler.get_answer_code(answer) if answer else None
        )


class CheckboxesFieldSerializer(FormFieldSerializer):

    value = serializers.ListField(child=serializers.CharField(max_length=1024), required=True, allow_null=True, source="answer")
    options = serializers.ListField(required=True)

    def create(self, validated_data: dict) -> CheckboxesField:
        answers = []
        for option in validated_data["options"]:
            multiple_choice_option_serializer = MultipleChoiceOptionSerializer(data=option)
            option = multiple_choice_option_serializer.save() if multiple_choice_option_serializer.is_valid() else None
            if option and option.choice_id in validated_data["answer"]:
                answers.append(option.text)

        return CheckboxesField(
            question=FormFieldHandler.get_question_code(validated_data["question"]),
            field_type=validated_data["field_type"],
            answer=[FormFieldHandler.get_answer_code(answer) for answer in answers] if answers else None
        )


class SurveyDataSerializer(serializers.Serializer):

    formId = serializers.CharField(max_length=1024, required=True, source="form_id")
    createdAt = serializers.DateTimeField(required=True, source="created_at")
    fields = serializers.ListField(required=True, source="answers")

    def create(self, validated_data: dict) -> SurveyData:
        answers = {}
        wenet_id = None
        for raw_field in validated_data["answers"]:
            try:
                answer = FormFieldHandler.build(raw_field)
                if isinstance(answer, HiddenField) and answer.question == "wenetId":
                    wenet_id = answer.answer
                else:
                    answers[answer.question] = answer
            except ValueError as e:
                logger.exception("", exc_info=e)

        if wenet_id is None:
            raise ValueError("No WeNet id was found in the form")

        survey_data = SurveyData(
            form_id=validated_data["form_id"],
            created_at=validated_data["created_at"],
            wenet_id=wenet_id,
            answers=answers
        )
        return survey_data

    def update(self, survey: SurveyData, validated_data: dict) -> SurveyData:
        raise NotImplemented()

    def to_representation(self, instance: SurveyData) -> dict:
        raw_fields = [FormFieldHandler.to_repr(instance.answers[key]) for key in instance.answers if FormFieldHandler.to_repr(instance.answers[key])]
        return {
            "formId": instance.form_id,
            "createdAt": instance.created_at,
            "wenetId": instance.wenet_id,
            "answers": raw_fields
        }


class SurveyEventSerializer(serializers.Serializer):

    eventType = serializers.RegexField(r"FORM_RESPONSE", required=True)
    data = serializers.DictField(required=True)

    def create(self, validated_data: dict) -> SurveyData:
        survey_data_serializer = SurveyDataSerializer(data=validated_data["data"])
        if survey_data_serializer.is_valid():
            return survey_data_serializer.save()
        else:
            raise ValueError(survey_data_serializer.errors)

    def update(self, survey: SurveyData, validated_data: dict) -> SurveyData:
        raise NotImplemented()

    def to_representation(self, instance: SurveyData) -> dict:
        survey_data_serializer = SurveyDataSerializer(instance=instance)
        return survey_data_serializer.data
