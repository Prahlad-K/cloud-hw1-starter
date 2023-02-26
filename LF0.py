import boto3
from datetime import datetime
import uuid
import random
client = boto3.client('lexv2-runtime')
def lambda_handler(event, context):
    
    msg_from_user = event['messages'][0]
    sessionID = event['sessionID']
    print(event)
    print("sessionID:",sessionID)
    # Session based check to ensure if we have data from db we render it as it is
    if sessionID == "":
        sessionID = "testuser" # In case invalid sessionID they are mapped to testuser
    
    print(f"Message from frontend: {msg_from_user}")
    # Initiate conversation with Lex
    try:
        response = client.recognize_text(
                botId='KWLYLAGIR8', # MODIFY HERE
                botAliasId='UXITOPHKUG', # MODIFY HERE
                localeId='en_US',
                sessionId=sessionID,
                text=msg_from_user['unstructured']['text'])
        
        print(response)

        if response['interpretations'][0]['intent']['name']== 'GreetingsIntent':
            if sessionID != "testuser":
                dbClient =  boto3.client('dynamodb')

                print("Fetching sessionID details from Dynamo DB")
                try:
                    resp1 = dbClient.get_item(TableName='sessionData',Key={'sessionID': {'S': sessionID}})
                    print(resp1)
                    messageList = list(resp1['Item']["content"]['S'].split('^'))
                    
                    messageListLen = len(messageList)
                    messageIndex = random.randint(0,messageListLen-1)
                    
                    respObj = {"messages":[{"type":"unstructured","unstructured":{"id":str(uuid.uuid4()),"text":"Here are you recommendations based on past "+ str(messageListLen) +" orders:\n\n"+messageList[messageIndex],"timestamp":str(datetime.now())}}]}
                    print(respObj)
                    resp = {
                            'statusCode': 200,
                            'body': respObj
                        }
                    return resp
                        
                except:
                    print("No sessionID details available in Dynamo DB")
                        

        
        
        msg_from_lex = response.get('messages', [])
        print(msg_from_lex)
        formatedMessage = []
        for msg in msg_from_lex:
            formatedMessage.append({"type":"unstructured","unstructured":{"id":str(uuid.uuid4()),"text":msg["content"],"timestamp":str(datetime.now())}})
        
        respObj = {"messages":formatedMessage}
        print(respObj)

        
        
        if msg_from_lex:
            
            print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
            print(response)
            resp = {
                'statusCode': 200,
                'body': respObj
            }
            # modify resp to send back the next question Lex would ask from the user
            
            # format resp in a way that is understood by the frontend
            # HINT: refer to function insertMessage() in chat.js that you uploaded
            # to the S3 bucket
        else:
            respObj = {"messages":[{"type":"unstructured","unstructured":{"id":str(uuid.uuid4()),"text":"Internal Server Error. ","timestamp":str(datetime.now())}}]}
            resp = {
                    'statusCode': 200,
                    'body': respObj
                }
        return resp
    except:
        respObj = {"messages":[{"type":"unstructured","unstructured":{"id":str(uuid.uuid4()),"text":"Internal Server Error. ","timestamp":str(datetime.now())}}]}
        resp = {
                'statusCode': 200,
                'body': respObj
            }
        return resp