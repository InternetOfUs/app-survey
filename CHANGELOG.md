# Changelog

## 0.*

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
