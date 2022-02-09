# Contribute

## Language support

### Adding support for a new language

In order to add the support for a new language, the following steps should be completed.

1. Add the new language code with the translation of the language in the `LANGUAGES` variable in the [settings.py](src/wenet_survey/settings.py) file.
```python
LANGUAGES = [
   ...
   ('<language code>', 'Your Language'),
]
```
2. In order to create the list of translation keys for a new language, use the following command (to be executed in the [src](src) folder where the file [manage.py](src/manage.py) lies):
```bash
django-admin makemessages -l <language code>
```
3. Edit the `django.po` file by translating the english texts (available in [src/locale/en/LC_MESSAGES/django.po](src/locale/en/LC_MESSAGES/django.po)) with the new languages translations. 
    * Only texts associated to the `msgstr` should be changed,
    * Labels associated to `msgid` should not be changed.
4. Once the changes are completed, compile the `django.po` file. This will generate a `django.mo` file. This can be done using the following command (to be executed in the [src](src) folder where the file [manage.py](src/manage.py) lies):
```bash
django-admin compilemessages -l <language code>
```
5. Go inside the [src/wenet_survey/mixin.py](src/wenet_survey/mixin.py) file and add the activation for the new language.
```python
        elif re.match(r"<language code>", locale):
            translation.activate("<language code>")
```
6. Create a new pull request with your proposed changes. Please, make sure to detail your changes in the description.

### Edit translations for an already supported language

In order to propose changes to the translation of an existing language, the following steps should be completed.

1. Browse in the [locale](src/locale) folder and into the folder of the language you would like to propose changes for.
2. Open the `django.po`.
3. Identify the text you would like to change the translation for and apply your changes.
4. Compile the changes into an updated `django.mo` file. This can be done using the following command (to be executed in the [src](src) folder where the file [manage.py](src/manage.py) lies):
```bash
django-admin compilemessages -l <language code>
```
5. Create a new pull request with your proposed changes. Please, make sure to deail your changes in the description.


## Survey support 

### Adding support for a new language

In order to add the support for the survey in a new language, the following steps should be completed.

1. Create a new survey following the instructions reported in: [https://internetofus.github.io/developer/docs/tech/usecase/survey-app](https://internetofus.github.io/developer/docs/tech/usecase/survey-app). Start from the provided template and translate it in the new language. Note that not all questions have to be translated. If the survey template contains questions that are not relevant to the purpose, it is possible not to include them.
2. Define a new environmental variable for the new survey identifier with the following structure: `SURVEY_FORM_ID_<LANGUAGE CODE>`.
3. Add this new environmental variable among the environment variables in the [README.md](README.md) file.
4. Add a new variable inside the [settings.py](src/wenet_survey/settings.py) file for reading your environmental variable:
```python
SURVEY_FORM_ID_<LANGUAGE CODE> = os.getenv("SURVEY_FORM_ID_<LANGUAGE CODE>")
```
5. Go inside the [src/survey/views/survey.py](src/survey/views/survey.py) file and add the selection of the survey in the new language.
```python
        elif re.match(r"<language code>", locale):
            form_id = settings.SURVEY_FORM_ID_<LANGUAGE CODE> 
```
6. Create a new pull request with your proposed changes. Please, make sure to detail your changes in the description and include the new survey identifier.
