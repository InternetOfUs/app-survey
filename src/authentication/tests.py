from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, Client
from wenet.model.user.profile import WeNetUserProfile
from wenet.model.user.token import TokenDetails


class TestHomeView(TestCase):

    def test_profile_with_empty_locale(self):
        with patch("wenet.interface.service_api.ServiceApiInterface.get_token_details") as mock_token_details:
            with patch("wenet.interface.service_api.ServiceApiInterface.get_user_profile") as mock_get_profile:
                settings.WENET_INSTANCE_URL = ""

                mock_token_details.return_value = TokenDetails("1", "1", [])
                mock_get_profile.return_value = WeNetUserProfile.empty("1")

                client = Client()
                session = client.session
                session["has_logged"] = True
                session["resource_id"] = "1"
                session.save()
                response = client.get("/")

                self.assertEqual(200, response.status_code)
                mock_get_profile.assert_called_once()
                mock_token_details.assert_called_once()
