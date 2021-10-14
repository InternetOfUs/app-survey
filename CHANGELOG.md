# Changelog

## 0.*

## 0.2.0

* Defined a rule for psycho-social profiles, integrated survey questions B01 and B02 in the code
* Updated common models to `3.0.0` and updated the `update_profile` task in order to manage the fields not in the core profile (materials, competencies, meanings)

### 0.1.0

* Set up the project with basic HTML pages.
* Added support to WeNet OAuth2 authentication flow.
* Integrated survey in the app.
* Created a web service for parsing survey responses.
* Set up the structure for updating a user profile.
* Added sentry integration
* Added periodic task to handle possible errors when updating the profile, every 15 minutes checks if there are errors and tries to re-execute the tasks that causes the errors
* Defined basic rule types, defined nationality and language inputs
* Integrated surveys in the code except A11 and Q06 questions and Psycho-social profiles (B01, B02)
