"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3
import datetime

dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id='AKIAIISHT6IO4KCJ25SQ',
    aws_secret_access_key='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',
    region_name='us-east-1'
    )

def fetchData():
    table = dynamodb.Table('Goals')
    response = table.scan()
    return response




def addData(goal,timeline):
    table = dynamodb.Table('Goals')
    table.put_item(
           Item={
               'goal': int(goal),
               'timeline': timeline,
              }
        )


def setupDB():


    try:
        table = dynamodb.create_table(
            TableName='Goals',
            KeySchema=[
                {
                    'AttributeName': 'goal',
                    'KeyType': 'HASH'  #Partition key
                },
                {
                    'AttributeName': 'timeline',
                    'KeyType': 'RANGE'  #Sort key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'goal',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'timeline',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )


    except:
        print("Table exists")
     # do something here as you require
        


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    #table = setupDB()

    #addData(table,3,"welcome")
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Alexa  Fitness Skills. " \
                    "Please tell me your goals  by saying, " \
                    "my goal is to burn 100 calories today"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your goal by saying, " \
                    "my goal is buring 100 calories today."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_goal_attributes(goal,timeline):
    return {
        "goal": goal,
        "timeline" : timeline
    }


def set_goal_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

   
    print(intent['slots'])

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'calories' in intent['slots']:
        goal = intent['slots']['calories']['value']
        timeline = intent['slots']['timeline']['value']
        addData(goal,timeline)
        session_attributes = create_goal_attributes(goal,timeline)
        #print(sessionAttributes)
        speech_output = "I now know your goal is " + \
                        goal + " calories "+timeline+ \
                        ". You can ask me your goals by saying, " \
                        "what's my goal?"
        reprompt_text = "You can ask me your goals by saying, " \
                        "what are my goals?"
    else:
        speech_output = "Unable to recognise your goal please be more precise " \
                        "Please try again."
        reprompt_text = "I'm not sure of your goal " \
                        "You can tell me your goal by saying, " \
                        "my goal is buring 100 calories today."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_calorie_from_session(intent, session):
    print("Getting calorie")
    session_attributes = {}
    reprompt_text = None

    if fetchData():
        response = fetchData()

    print(response)
    total_calorie = 0 
    for i in response['Items']:
        if "today" in str(i):
            print(i['goal'])
            total_calorie= total_calorie+i['goal']

    speech_output = "total calorie of today is " +str(total_calorie) 
    should_end_session = True

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))



def get_goal_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    # if session.get('attributes', {}) and "goal" in session.get('attributes', {}):
    #     goal = session['attributes']['goal']
    #     timeline = session['attributes']['timeline']
    #     speech_output = "Your goal is " + goal +" calories in "+timeline+ \
    #                     ". Goodbye."
    #     should_end_session = True

    if fetchData():
        response = fetchData()
        array = []
        for i in response['Items']:
            array.append("Your goal is "+str(i['goal']) +" calories for "+str(i['timeline'])+", ")

        speech_output = ''.join(array)
        should_end_session = True
        
    else:
        speech_output = "I'm not sure what your goal is. " \
                        "You can say, my goal is burning 100 calories."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    try:
        table = setupDB()
    except Exception, e:
        print(e) 
    
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    print(intent_request['intent'])     
    print(intent_request['intent']['name'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    print(intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "SetGoal":
        return set_goal_in_session(intent, session)
    elif intent_name == "ListGoals":
        return get_goal_from_session(intent, session)

    elif intent_name == "GetCalorie":
        return get_calorie_from_session(intent, session)

    elif intent_name == "LogCalorie":
        return log_calorie_from_session(intent, session)

    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        #raise ValueError("Invalid intent")
        print("No intent found")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
