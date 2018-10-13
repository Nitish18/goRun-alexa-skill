import json
import random
from botocore.vendored import requests


def lambda_handler(event, context):

    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.50553467-6730-4f71-96c3-5186d0d569c2"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    try:
        access_token = event['context']['System']['user']['accessToken']
    except:
        access_token = None

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"], access_token)
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])


def on_session_started(session_started_request, session):
    print("Starting new session.")


def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session, access_token):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    # custom intents
    if intent_name == "invocation_intent":
        return get_intro()

    elif intent_name == "get_marathon_data":
        return cal_marathon_data(intent, session, intent_request, access_token)

    # predefined intents
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...


def handle_session_end_request():
    session_attributes = {}
    card_title = "gorun - Thanks"
    speech_output = "Thank you for using gorun. See you next time!"

    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_welcome_response():
    session_attributes = {}
    card_title = "GO RUN"
    speech_output = "Welcome to the Alexa gorun skill. " \
                    "If you feel like running I can help you find some running events across different cities near you"

    reprompt_text = "If you feel like running I can help you find some running events across different cities."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_intro():
    session_attributes = {}
    card_title = "Alexa gorun skill"
    reprompt_text = ""
    should_end_session = False
    speech_output = "Hi there !! Welcome to GoRun, if you feel like running I can help you find some running events across different cities."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def continue_dialog():
    message = {}
    session_attributes = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(session_attributes, message)


def get_user_info(access_token):
    # print access_token
    amazonProfileURL = 'https://api.amazon.com/user/profile?access_token='
    try:
        r = requests.get(url=amazonProfileURL + access_token)
        if r.status_code == 200:
            return r.json()
        return False
    except Exception as e:
        return False


def cal_marathon_data(intent, session, intent_request, access_token):
    session_attributes = {}
    card_title = "Getting marathon data near you"
    speech_output = "sorry, can you please try again !!"
    reprompt_text = "sorry, can you please try again !!"
    should_end_session = True
    dialog_state = intent_request['dialogState']
    user_intent_confirm_status = intent_request.get('intent', {}).get('confirmationStatus')

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()
    elif dialog_state == "COMPLETED":

        if user_intent_confirm_status in ['DENIED']:
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, False))

        if "slots" in intent and "city" in intent["slots"] and "event_type" in intent["slots"] and "date_range" in intent["slots"]:
            city = intent["slots"]["city"].get('value')
            event_type = intent["slots"]["event_type"].get('value')
            date_range = intent["slots"]["date_range"].get('value')

            # calling API to fetch data
            api_base_url = "https://alexa-gorun-skill.herokuapp.com/get_marathon_data?Cities=" + \
                str(city) + '&type1=' + str(event_type) + '&DateRange=' + str(date_range)
            res = requests.get(api_base_url)

            if res.status_code in [200]:
                res_count = len(res.json().get('data', []))
                session_attributes = {}
                card_title = "Here are some running events for you"

                data_list = res.json().get('data', [])

                event_list = ""
                for i, j in enumerate(data_list):
                    if i > 3:
                        break
                    event_list = event_list + str(j.get('Event')) + \
                        ' on ' + str(j.get('Date')) + '. '

                speech_output = "I have found out " + str(res_count) + " events near you."

                if event_list:
                    speech_output = speech_output + " Some of them are : " + event_list

                reprompt_text = "Would you like to search again ??"
                should_end_session = False
                return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
            return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    else:
        return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
