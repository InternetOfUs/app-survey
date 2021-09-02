from __future__ import absolute_import, annotations

from datetime import datetime
from unittest.mock import Mock

from django.db import transaction
from django.test import TestCase

from tasks.models import FailedProfileUpdateTask, LastUserProfileUpdate
from tasks.tasks import ProfileHandler, update_user_profile, recover_profile_update_error
from ws.models.survey import SurveyAnswer, SingleChoiceAnswer


class TestCeleryTask(TestCase):

    def test_update_user_profile(self):
        ProfileHandler.update_profile = Mock()
        survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
        update_user_profile(survey_answer.to_repr())
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_update_user_profile_exception(self):
        ProfileHandler.update_profile = Mock(side_effect=Exception())
        survey_answer = SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")})
        update_user_profile(survey_answer.to_repr())
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error(self):
        ProfileHandler.update_profile = Mock()
        with transaction.atomic():
            last_user_profile_update = LastUserProfileUpdate(
                wenet_id="wenetId",
                last_update=datetime.now()
            )
            last_user_profile_update.save()

        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_exception(self):
        ProfileHandler.update_profile = Mock(side_effect=Exception())
        with transaction.atomic():
            last_user_profile_update = LastUserProfileUpdate(
                wenet_id="wenetId",
                last_update=datetime.now()
            )
            last_user_profile_update.save()

        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_failed_update(self):
        ProfileHandler.update_profile = Mock()
        recover_profile_update_error(SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr())
        ProfileHandler.update_profile.assert_not_called()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_profile_update(self):
        ProfileHandler.update_profile = Mock()
        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(1, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_without_profile_update_exception(self):
        ProfileHandler.update_profile = Mock(side_effect=Exception())
        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        ProfileHandler.update_profile.assert_called_once()
        self.assertEqual(1, len(FailedProfileUpdateTask.objects.all()))
        self.assertEqual(0, len(LastUserProfileUpdate.objects.all()))

    def test_recover_profile_update_error_old(self):
        ProfileHandler.update_profile = Mock()
        with transaction.atomic():
            failed_profile_update_task = FailedProfileUpdateTask(
                wenet_id="wenetId",
                raw_survey_answer=SurveyAnswer(wenet_id="wenetId", answers={"A01": SingleChoiceAnswer("A01", SingleChoiceAnswer.FIELD_TYPE, "5")}).to_repr(),
                failure_datetime=datetime.now()
            )
            failed_profile_update_task.save()

        with transaction.atomic():
            last_user_profile_update = LastUserProfileUpdate(
                wenet_id="wenetId",
                last_update=datetime.now()
            )
            last_user_profile_update.save()

        recover_profile_update_error(failed_profile_update_task.raw_survey_answer)
        ProfileHandler.update_profile.assert_not_called()
        self.assertEqual(0, len(FailedProfileUpdateTask.objects.all()))
