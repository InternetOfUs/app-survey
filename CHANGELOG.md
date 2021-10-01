# Changelog

## 0.*

### next

* Set up the project with basic HTML pages.
* Added support to WeNet OAuth2 authentication flow.
* Integrated survey in the app.
* Created a web service for parsing survey responses.
* Set up the structure for updating a user profile.
* Added sentry integration
* Added periodic task to handle possible errors when updating the profile, every 15 minutes checks if there are errors and tries to re-execute the tasks that causes the errors
* Defined basic rule types, defined nationality and language inputs
* Integrated surveys in the code except A11 and Q06 questions and Psycho-social profiles