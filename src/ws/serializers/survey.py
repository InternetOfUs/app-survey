from __future__ import absolute_import, annotations

from rest_framework import serializers

from ws.models.survey import SurveyEvent, SurveyData, FormField, HiddenField, MultipleChoiceOption, NumberField, \
    LinearScaleField, RatingField, MultipleChoiceField, DropdownField, CheckboxesField


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


class FormFieldSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1024, required=True)
    label = serializers.CharField(max_length=1024, required=True)
    type = serializers.CharField(max_length=1024, required=True, source="field_type")
    value = serializers.Field(required=True)
    options = MultipleChoiceOptionSerializer(many=True, required=False)

    def create(self, validated_data: dict) -> FormField:
        if validated_data["field_type"] == HiddenField.FIELD_TYPE:
            form_field = HiddenField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
            )
        elif validated_data["field_type"] == NumberField.FIELD_TYPE:
            form_field = NumberField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
            )
        elif validated_data["field_type"] == LinearScaleField.FIELD_TYPE:
            form_field = LinearScaleField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
            )
        elif validated_data["field_type"] == RatingField.FIELD_TYPE:
            form_field = RatingField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
            )
        elif validated_data["field_type"] == MultipleChoiceField.FIELD_TYPE:
            form_field = MultipleChoiceField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
                options=validated_data["options"]
            )
        elif validated_data["field_type"] == DropdownField.FIELD_TYPE:
            form_field = DropdownField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
                options=validated_data["options"]
            )
        elif validated_data["field_type"] == CheckboxesField.FIELD_TYPE:
            form_field = CheckboxesField(
                key=validated_data["key"],
                label=validated_data["label"],
                field_type=validated_data["field_type"],
                value=validated_data["value"],
                options=validated_data["options"]
            )
        else:
            raise ValueError("Unsupported type of form field")

        return form_field

    def update(self, survey: FormField, validated_data: dict) -> FormField:
        raise NotImplemented()


class SurveyDataSerializer(serializers.Serializer):

    responseId = serializers.CharField(max_length=1024, required=True, source="response_id")
    respondentId = serializers.CharField(max_length=1024, required=True, source="respondent_id")
    formId = serializers.CharField(max_length=1024, required=True, source="form_id")
    formName = serializers.CharField(max_length=1024, required=True, source="form_name")
    createdAt = serializers.DateTimeField(max_length=1024, required=True, source="created_at")
    fields = FormFieldSerializer(many=True, required=True, source="created_at")

    def create(self, validated_data: dict) -> SurveyData:
        survey_data = SurveyData(
            response_id=validated_data["response_id"],
            respondent_id=validated_data["respondent_id"],
            form_id=validated_data["form_id"],
            form_name=validated_data["form_name"],
            created_at=validated_data["created_at"],
            fields=validated_data["fields"]
        )
        return survey_data

    def update(self, survey: SurveyData, validated_data: dict) -> SurveyData:
        raise NotImplemented()


class SurveyEventSerializer(serializers.Serializer):

    eventId = serializers.CharField(max_length=1024, required=True, source="event_id")
    eventType = serializers.CharField(max_length=1024, required=True, source="event_type")
    createdAt = serializers.DateTimeField(required=True, source="created_at")
    data = SurveyDataSerializer(required=True, source="data")

    def create(self, validated_data: dict) -> SurveyEvent:
        survey = SurveyEvent(
            event_id=validated_data["event_id"],
            event_type=validated_data["event_type"],
            created_at=validated_data["created_at"],
            data=validated_data["data"]
        )
        return survey

    def update(self, survey: SurveyEvent, validated_data: dict) -> SurveyEvent:
        raise NotImplemented()
