# Changelog

## Version 0.*

### 0.4.0
:rocket: New features
* Updated the supported set of question to be compliant with the M46 Pilot

:house: Internal
* Moved deployment outside the repository

### 0.3.8

:nail_care: Polish
* The update task is now able to handle the cases in which na user has only provided a subset of the required scopes.
* Now the update of a profile i re-tried only a configurable number of times

:bug: Bug fixes
* Fixed question parsing, the music question was associated to the wrong id.

:house: Internal
* Updated the wenet common library to 5.0.0
* Updated to project template version 4.12.5

### 0.3.7

* Fixed traefik configuration

### 0.3.6

* Fixed bug in updating key of cashing credentials

### 0.3.5

* Updated methods for caching and updating credentials in order to ensure that only an object at the time is present in the database
* Updated project template to version `4.6.1`

### 0.3.4

* Fixed bug: now the update of the profile does not crash when a user has an empty date of birth
* Updated project template to version `4.6.0`
* Added the `SENTRY_SAMPLE_RATE` env variable in order to control the number of transactions stored in sentry

### 0.3.3

* Fixed bug: now the survey does not crash when a user as an empty locale

### 0.3.2

* Updated survey id for spanish language

### 0.3.1

* Fixed docker-compose template

### 0.3.0
* Defined the rule for university (pilot) selection
* Updated the survey with the departments and degrees regarding the pilots

### 0.2.3
* Updated the AAU department list with the final version

### 0.2.2
* Changed pre-pilot department list from LSE to AAU

### 0.2.1

* Updated some wrong profile attributes in rules
* Retrieved the existing competences, materials and meanings before updating them
* Added a sleep time in order to avoid overloading the profile manager that causes the service APIs to send us a 500 status code when updating profile fields

### 0.2.0

* Defined a rule for psycho-social profiles, integrated survey questions B01 and B02 in the code
* Updated common models to `3.1.0` and updated the `update_profile` task in order to manage the fields not in the core profile (materials, competencies, meanings)
* Edited the survey with Q01 to Q09 questions
* Fixed a bug related to division by zero in questions
* Fixed a bug related to label set to None in the data from tally

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
