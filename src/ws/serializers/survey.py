from __future__ import absolute_import, annotations

from typing import Optional

from rest_framework import serializers

from ws.models.survey import SurveyEvent, SurveyData, FormField, HiddenField, MultipleChoiceOption, NumberField, \
    LinearScaleField, RatingField, MultipleChoiceField, DropdownField, CheckboxesField, DateField


class FormFieldHandler:

    @staticmethod
    def to_repr(form_field: FormField) -> Optional[dict]:
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

    @staticmethod
    def build(raw_field: dict) -> Optional[FormField]:
        if raw_field["type"] == HiddenField.FIELD_TYPE:
            serializer = HiddenFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == NumberField.FIELD_TYPE:
            serializer = NumberFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == DateField.FIELD_TYPE:
            serializer = DateFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == LinearScaleField.FIELD_TYPE:
            serializer = LinearScaleFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == RatingField.FIELD_TYPE:
            serializer = RatingFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == MultipleChoiceField.FIELD_TYPE:
            serializer = MultipleChoiceFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == DropdownField.FIELD_TYPE:
            serializer = DropdownFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()
        elif raw_field["type"] == CheckboxesField.FIELD_TYPE:
            serializer = CheckboxesFieldSerializer(data=raw_field)
            if serializer.is_valid():
                return serializer.save()


class HiddenFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.CharField(max_length=1024, required=True)

    def create(self, validated_data: dict) -> HiddenField:
        return HiddenField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
        )

    def update(self, multiple_choice_option: HiddenField, validated_data: dict) -> HiddenField:
        raise NotImplemented()


class NumberFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.IntegerField(required=True)

    def create(self, validated_data: dict) -> NumberField:
        return NumberField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
        )

    def update(self, multiple_choice_option: NumberField, validated_data: dict) -> NumberField:
        raise NotImplemented()


class DateFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.DateField(required=True)

    def create(self, validated_data: dict) -> DateField:
        return DateField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
        )

    def update(self, multiple_choice_option: DateField, validated_data: dict) -> DateField:
        raise NotImplemented()


class LinearScaleFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.IntegerField(required=True)

    def create(self, validated_data: dict) -> LinearScaleField:
        return LinearScaleField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
        )

    def update(self, multiple_choice_option: LinearScaleField, validated_data: dict) -> LinearScaleField:
        raise NotImplemented()


class RatingFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.IntegerField(required=True)

    def create(self, validated_data: dict) -> RatingField:
        return RatingField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
        )

    def update(self, multiple_choice_option: RatingField, validated_data: dict) -> RatingField:
        raise NotImplemented()


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


class MultipleChoiceFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.CharField(max_length=1024, required=True)
    options = MultipleChoiceOptionSerializer(many=True, required=False)

    def create(self, validated_data: dict) -> MultipleChoiceField:
        return MultipleChoiceField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
            options=validated_data["options"]
        )

    def update(self, survey: MultipleChoiceField, validated_data: dict) -> MultipleChoiceField:
        raise NotImplemented()


class DropdownFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.CharField(max_length=1024, required=True)
    options = MultipleChoiceOptionSerializer(many=True, required=False)

    def create(self, validated_data: dict) -> DropdownField:
        return DropdownField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
            options=validated_data["options"]
        )

    def update(self, survey: DropdownField, validated_data: dict) -> DropdownField:
        raise NotImplemented()


class CheckboxesFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.ListField(child=serializers.CharField(max_length=1024), required=True)
    options = MultipleChoiceOptionSerializer(many=True, required=False)

    def create(self, validated_data: dict) -> CheckboxesField:
        return CheckboxesField(
            key=validated_data["key"],
            label=validated_data["label"],
            field_type=validated_data["field_type"],
            value=validated_data["value"],
            options=validated_data["options"]
        )

    def update(self, survey: CheckboxesField, validated_data: dict) -> CheckboxesField:
        raise NotImplemented()


class SurveyDataSerializer(serializers.Serializer):

    responseId = serializers.CharField(max_length=1024, required=True, source="response_id")
    respondentId = serializers.CharField(max_length=1024, required=True, source="respondent_id")
    formId = serializers.CharField(max_length=1024, required=True, source="form_id")
    formName = serializers.CharField(max_length=1024, required=True, source="form_name")
    createdAt = serializers.DateTimeField(required=True, source="created_at")
    fields = serializers.ListField(required=True)

    def create(self, validated_data: dict) -> SurveyData:
        fields = [FormFieldHandler.build(raw_field) for raw_field in validated_data["fields"] if FormFieldHandler.build(raw_field)]
        survey_data = SurveyData(
            response_id=validated_data["response_id"],
            respondent_id=validated_data["respondent_id"],
            form_id=validated_data["form_id"],
            form_name=validated_data["form_name"],
            created_at=validated_data["created_at"],
            fields=fields
        )
        return survey_data

    def update(self, survey: SurveyData, validated_data: dict) -> SurveyData:
        raise NotImplemented()

    def to_representation(self, instance: SurveyData) -> dict:
        raw_fields = [FormFieldHandler.to_repr(field) for field in instance.fields if FormFieldHandler.to_repr(field)]
        return {
            "responseId": instance.response_id,
            "respondentId": instance.respondent_id,
            "formId": instance.form_id,
            "formName": instance.form_name,
            "createdAt": instance.created_at.isoformat(),
            "fields": raw_fields
        }


class SurveyEventSerializer(serializers.Serializer):

    eventId = serializers.CharField(max_length=1024, required=True, source="event_id")
    eventType = serializers.CharField(max_length=1024, required=True, source="event_type")
    createdAt = serializers.DateTimeField(required=True, source="created_at")
    data = serializers.DictField(required=True)

    def create(self, validated_data: dict) -> SurveyEvent:
        survey_data_serializer = SurveyDataSerializer(data=validated_data["data"])
        survey = SurveyEvent(
            event_id=validated_data["event_id"],
            event_type=validated_data["event_type"],
            created_at=validated_data["created_at"],
            data=survey_data_serializer.save() if survey_data_serializer.is_valid() else None
        )
        return survey

    def update(self, survey: SurveyEvent, validated_data: dict) -> SurveyEvent:
        raise NotImplemented()

    def to_representation(self, instance: SurveyEvent) -> dict:
        survey_data_serializer = SurveyDataSerializer(instance=instance.data)
        return {
            "eventId": instance.event_id,
            "eventType": instance.event_type,
            "createdAt": instance.created_at.isoformat(),
            "data": survey_data_serializer.data
        }
