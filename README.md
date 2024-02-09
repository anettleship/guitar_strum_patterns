# Guitar Strum Pattern Generator Web App
Web application built to render simple guitar strumming patterns:

## Instructions to install and run on a local machine using the Flask inbuilt testing server:

Install Python 3.12:
https://www.python.org/downloads/
Choose to add Python to Path

Verify python is installed by running `python` from a terminal session, it may be necessary to restart your terminal session or reboot your machine if you have never installed python before. 

Clone repository using git to local machine.

`git clone https://github.com/anettleship/guitar_strum_patterns.git`

Using your terminal, cd into the project folder adrian-al-testtest-app.

`cd guitar_strum_patterns`

Install pipenv for python 3:

`pip3 install pipenv`

(On some platforms, this may need to be pip, rather than pip3).

We now need to create a virtual environment for our project, with the correct version of python and download and install dependencies as listed in pipenv file:

`pipenv install`

We are using python 3.12, and this is specified in the pipenv Pipfile included with the project. If installed correctly, this python version will be picked up by pipenv and used to make our virtual environment. If not, pipenv will throw an error. In this case, try reinstalling the correct python version, paying attention to the install location and adding it to your path. You may also need to reboot your machine.

Make a note of the location of the virtual environment that's created. If you are using an IDE, you will need to configure your IDE to use the correct virtual environment. IDE specific instructions are outside this document's scope, for testing purposes we can use the terminal.

Elevate the terminal so that our commands are executed in the contect of the virtual environment, with our project specific python version and dependencies:

`pipenv shell`

All python commands below must be run within a shell which has been elevated by running 'pipenv shell' first. Run `python` (on some systems this is `python3`).

We must now generate an app secret key (used to encrypt application data stored in the user's session cookie). Run the following commands sequentially within an interactive session and then copy the result to use in the next step:

`python`

`>>> import secrets`

`>>> secrets.token_urlsafe(16)`

`exit()`

Now we need to setting environment variables. Within the project structure is a folder named env_templates. Copy the template.env file into the root of the project (place next to app.py) and rename it to .env

`cp env_templates/template.env .env`

Then edit the file to manually insert the correct values for our application secret key: SECRET_KEY="" and the subscription key (included in requests to the external API that returns patient data from an NHS number, provided separately on request by the api owners): SUBSCRIPTION_KEY="" in between the quotes.

At this point, if you are deploying to production, change the variable STAGE from "development" to "production". This will cause our flask app to be loaded with debugging disabled.

We can verify the .env is being loaded successfully by running the following to view our secret key:

`python`

`>>> from dotenv import load_dotenv`

`>>> load_dotenv()`

`>>> import os`

`>>> os.environ.get("SECRET_KEY")`

`exit()`

Note, that my prefered choice for secrets such as secret keys and api keys would be a service like AWS Secrets Manager, as it solves the problem of how to deploy these secrets safely to other environments and share between developers. For simplicity in this project, we place these secrets in our .env file manually when setting up the project. 

Production deployment is outside the scope of this document, but note that it will be necessary to ensure these environment values are set on any machine which runs our service.

Now we have set up our environment variables, still running within our virtual environment terminal, at the root of our project directory, elevated by running pipenv shell earlier, we can run the following to run our tests:

`pytest`

If any tests fail, the most likely issue is a missing or misplaced yaml cassette recording of an api request. Try running the following to create missing recordings by accessing the live api once:

`pytest --record-mode=once`

If all tests pass, we can then run the following to start our testing server. Note the web address where this is being served and navigate to this URL from a web browser, to access our application e.g. http://127.0.0.1:5000:

`flask run`

## High Level Design:

This is a Flask application implemented with an app_factory to instantiate apps with different settings for testing, development and production. It is implemented with a single blueprint, to keep the application itself separate from the component: strumpatterns that addresses our requirements.

We use pipenv for virtual environment management, python-dotenv for environment variables management from a .env file, pytest for testing and requests to call our external api.  For frontend we use bootstrap to simplify css layout. 

I chose Flask in favour of Django because it results in a ligher weight codebase, can be stood up faster, and because the requirements ask for a simple application and do not specify the need for a database.

We're using pytest-recording to 'playback' api responses from the external api for our tests rather than testing against the live external api.

When adding or changing tests with the @pytest.mark.vcr(filter_headers=(["Ocp-Apim-Subscription-Key"])) decorator, it is necessary to run the following command to place a live request to the external api and record the result for any tests which do not have a matching 'recording' in the tests/cassettes folder. These are provided in the package, so the following command is not necessary in order to run tests if no changes are made to them.

pytest --record-mode=once

See https://github.com/kiwicom/pytest-recording for more info.

We have pytest-cov in our development dependencies, to check test coverage. This is not set up to run automatically, as this would slow down running our tests. This can be run manually by installing development packages from our piplock file and then using the following command with a shell elevated to the virtual environment. This is not necessary to run the application itself.

`pipenv install --dev`

Once installed run:

`pytest --cov` 

This will run tests and produce a report displaying current test coverage. The file 'setup.cfg' includes settings that control pytest-cov, most importantly, setting it up to check for branch coverage.

For cases in the application where a response or validation can include one of a number of possible values, I have used enums to store these possibilities, and to communicate these values within tests. As opposed to passing a string or dictionary directly, which can take any value, the use of enums limits the possible states of these values to the discrete items set. These are stored in strumpatterns_config.py.

## Application Flow

The t2lilfestylechecker blueprint is set up to start from the root of the application. The user is presented with a login form from the "/" route. 

On entering correct details, these are posted to the "generate" route, which handles placing a call to the external api configured in environment variables. Code for these operations is contained in the ExternalValidationHandler class, which is initialised with data from the form post, and which will query the external api when the validate_details() method is called. 

On successful validation, the user is logged in and their age saved to the flask session object for later. They are then redirected to a questionnaire, or a failure message if the details provided do not match the conditions specified in the requirements document. 

The "questionnaire" route returns a second form, which asks the user questions about their lifestyle. It loads questionnaire data from a static json file, which includes all the questionnaire text and inputs for displaying a questionnaire and calculating the user's score and message in response to their form input. This is packaged together in the QuestionnaireHandler class, which is initialised with a parameter for the path to the questionnaire json data file in t2lifestlyechecker/question_data/default_question_data.json.

The "questionnaire" route calls one final route, posting the user's answers to the form to the "calculate_score" route. This uses the calculate_message() method of the QuestionnaireHandler to return a message to the user, given their age and form answers. This message is rendered to a page, and the user is advised either to keep up the good work, or call for an appointment.

## Flask Application Initialisation

To initialise our Flask app, both when running the app and when performing automated testing, we run the create_app() function from application/app_factory.py. This function accepts a single argument, which is an instance of the class Config, defined in application/config.py. This Class loads values from our environment variables, or in the case of testing, accepts a string argument containing the name of the stage, which is one of three values set in an enum in the file application/config_stages.py: testing, development and production. Our create_app() function registers our strumpatterns blueprint to the root prefix "/" and also initialises basic authentication support. The required chain of events to start and run our application are contained within the app.py file in the root of our project.

## File Structure

See file_structure.txt for an annotated list of folder heirarchies and the purpose of individual files.

## Part 3 Requirements - Changing Questionnaire, Age Thresholds and Points without redeployment

I have implemented the questionnaire data in a separate json file with the Part 3 requirements in mind. If it were required to edit the questionnaire, these adjustments could be made to the json data, which includes a list of the points allocated for a given answer for each age range, and list of age range thresholds which set the maximum age for which the corresponding points score at the same index for any given answer applies. Taking a simple example:

age_range_thresholds = [16,64]
answer_score = [0,10,20]

For the the settings above, someone up to and including age 16 would get a score of 0 for this answer, 17 - 64 inclusive would get 10 points, and greater than 64, i.e. 65+ would get a score of 20. 

Similarly the message thresholds list sets the maximum points for which a message of that index applies.

Options to build out the solution to part 3 more fully would require a mechanism to edit these values and validate them. The simplest would be to create a route to allow the json to be edited directly by an admin user, and saved to a new file. Greater levels of complexity would include a UI with form validation that allows an admin user to enter questions. I have implemented some validation of the loaded json file in the QuestionnaireHandler method named validate_question_data() and a more thorough list might include checks for the following:

* any answer points length does not match age range maximums list + 1 i.e. there is not a points score defined for every age range for any given questionnaire answer.
* no min age
* input numerical values not int
* no age range maximums set
* age range maximums not int
* age range maxiumums not sorted low to high
* no questions property set
* questions length is 0
* question missing any of name, text, answers, and check if any fields length is 0
* length of message maximums needs to be one less than length of messages list
* json trailing commas
* messages['states'] and dictionaries for each language match

It might at this point be more logical to unpack the json data we load into properties on the class, rather than leaving it as json data, as this would force a more thorough validation on the incoming data and facilitate giving accurate feedback to the admin user on the source of any issue with the input data.

In the application, I have also demonstrated a partial implementation of language localisations. This includes an environment variable set to en-gb entries in the messages section of the default_question_data.json mapping to this code. Other languages could be included here, with entries corresponsding to the preset list of 'states' defined in our json. Similarly, our external_validation_handler_helper includes a dictionary externalvalidationhandler_message_localisations, against which messages for a given login_result can be looked up. As the application stands, I have not currently implemented multiple languages for Questions text in our questionnaire. Also currently, our languagei is set as a environment variable for the full application scope, which would be better refactored to set language in the user session, or as part of the base path of the route, allowing different users to use the app in different languages simultaneously. On this same point, the titles of our forms are currently stored as environment variables. They would be better placed together with localised form fields text as a series of xml or json files if the language use case were to be built out. 

## Additional Features

Some additional features I would build out were I to spend more time on the project include:

* Client side validation of Login Form input e.g. to reject blank or invalid inputs like future dates.
* Feedback to the client while the external api is being called, perhaps as simple as an animation made visible by client side code while the flask application calls the external api and redirects the client.
* The next logical step would be to move the call to the external api to an asyncronous call, so the flask application can return a response immediately to acknowledge the user's input, rather than locking up while waiting for the external api. Client side code could poll a separate route to display the results to the user when the async call has completed.
* The application has no logging currently, it might be useful to detect when users are trying and failing to log in, in case of issues with the external api. We need to be careful about whether or how we store personal data in such a scenario.
