
import boto3
from datetime import datetime, timezone, timedelta

def validate_slots(slots):

    if slots['DiningDate']:
        try:
            if 'interpretedValue' in slots['DiningDate']['value']:
                date_str = slots['DiningDate']['value']['interpretedValue']
                date_provided = datetime.strptime(date_str, '%Y-%m-%d').date()

                timeInNewYork = datetime.now(timezone(timedelta(hours=-5)))
                print(timeInNewYork.date().strftime("%Y-%m-%d"))
                if date_provided < timeInNewYork.date():
                    return {
                    'isValid' : False,
                    'invalidSlot': 'DiningDate',
                    'message' : 'The provided date, ' + date_provided.strftime("%Y-%m-%d") + ', is in the past. Please enter a valid date.'
                    }
            else:
                return {
                    'isValid' : False,
                    'invalidSlot': 'DiningDate',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid date.'
                    }
        except:
            return {
                    'isValid' : False,
                    'invalidSlot': 'DiningDate',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid date.'
                    }

    if slots['DiningTime']:
        try:
            if 'interpretedValue' in slots['DiningTime']['value']:
                time_str = slots['DiningTime']['value']['interpretedValue']
                time_provided = datetime.strptime(time_str, '%H:%M').time()

                date_str = slots['DiningDate']['value']['interpretedValue']
                date_provided = datetime.strptime(date_str, '%Y-%m-%d').date()

                datetime_provided = datetime.combine(date_provided, time_provided).replace(tzinfo=timezone(timedelta(hours=-5)))
                datetimeInNewYork = datetime.now(timezone(timedelta(hours=-5))).replace(second=0, microsecond=0)

                print(datetime_provided.strftime("%m/%d/%Y, %H:%M:%S, %Z"))
                print(datetimeInNewYork.strftime("%m/%d/%Y, %H:%M:%S, %Z"))
                
                if datetime_provided < datetimeInNewYork:
                    return {
                    'isValid' : False,
                    'invalidSlot': 'DiningTime',
                    'message' : 'The provided time, ' + time_provided.strftime("%H:%M") + ', is in the past. Please enter a valid time.'
                    }
            else:
                return {
                    'isValid' : False,
                    'invalidSlot': 'DiningTime',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid time.'
                    }
        except:
            return {
                    'isValid' : False,
                    'invalidSlot': 'DiningTime',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid time.'
                    }
    if slots['People']:
        try:
            if 'interpretedValue' in slots['People']['value']:
                number_people = int(slots['People']['value']['interpretedValue'])
                if number_people <= 0:
                    return {
                    'isValid' : False,
                    'invalidSlot': 'People',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid number of people.'
                    }
            else:
                return {
                    'isValid' : False,
                    'invalidSlot': 'People',
                    'message' : 'I couldn\'t quite get that. Kindly re-enter a valid number of people.'
                    }
        except:
            return {
                'isValid' : False,
                'invalidSlot': 'People',
                'message' : 'I couldn\'t quite get that. Kindly re-enter a valid number of people.'
                }
    return { 'isValid' : True}

def constructMessage(slots, sessionID):
    message = {}
    message['sessionID'] = {'StringValue' : sessionID, 'DataType' : 'String'}
    for slot in slots.items():
        valueDict = {}
        valueDict['StringValue'] = slot[1]['value']['interpretedValue']
        valueDict['DataType'] = 'String'
        message[slot[0]] = valueDict
    
    return message

def send_to_sqs(message):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='MessageQueue')
    response = queue.send_message(MessageBody='boto3', MessageAttributes=message)
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))
    print('Message sent to SQS successfully')

def lambda_handler(event, context):
    
    invocationSource = event['invocationSource']

    intent = event['sessionState']['intent']['name']
    print(intent)
    slots = event['sessionState']['intent']['slots']
    print(slots)

    if invocationSource == 'DialogCodeHook':
        print('DialogCodeHook')
        
        if intent == 'DiningSuggestionsIntent':

            validation_result = validate_slots(slots)

            if not validation_result['isValid']:
                if 'message' in validation_result:
                    response = {
                        "sessionState" : {
                            "dialogAction" : {
                                "slotToElicit" : validation_result['invalidSlot'],
                                "type" : "ElicitSlot"
                            },
                        "intent" : {
                            "name" : intent,
                            "slots" : slots
                            }
                        },
                        "messages" : [
                            {
                                "contentType" : "PlainText",
                                "content" : validation_result['message']
                            }
                        ]
                    }
                else:
                    response = {
                        "sessionState" : {
                            "dialogAction" : {
                                "slotToElicit" : validation_result['invalidSlot'],
                                "type" : "ElicitSlot"
                            },
                        "intent" : {
                            "name" : intent,
                            "slots" : slots
                            }
                        }
                    }
            else:
                print('All is well.')
                response = {
                    "sessionState" : {
                            "dialogAction" : {
                                "type" : "Delegate"
                            },
                        "intent" : {
                            "name" : intent,
                            "slots" : slots
                        }
                    }
                }
        # for any other intent, simply delegate
        else:
            print('Delegating because it is another intent.')
            response = {
                    "sessionState" : {
                            "dialogAction" : {
                                "type" : "Delegate"
                            },
                        "intent" : {
                            "name" : intent,
                            "slots" : slots
                        }
                    }
                }
    
    if invocationSource == 'FulfillmentCodeHook':
        print('FulfillmentCodeHook')
        message = constructMessage(slots, event['sessionId'])
        print("Message: ", message)
        send_to_sqs(message)
        response = {
                    "sessionState" : {
                            "dialogAction" : {
                                "type" : "Close"
                            },
                        "intent" : {
                            "name" : intent,
                            "slots" : slots,
                            "state" : "Fulfilled"
                        }
                    }
                }
    
    print("Response from LF1: ", response)
    return response