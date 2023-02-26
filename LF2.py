import json
import boto3
from datetime import datetime
import logging
from string import Template
import requests
import random


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def fetchMessageFromMQ():
    sqsClient = boto3.client('sqs')
    sqsUrl = 'https://sqs.us-east-1.amazonaws.com/626235363664/MessageQueue'
    
    # response picking up a message from SQS
    
    try:
        logger.debug("Starting the call to SQS")
        response = sqsClient.receive_message(QueueUrl =  sqsUrl, AttributeNames = ['All'] ,MessageAttributeNames=['All'],MaxNumberOfMessages  =1 , VisibilityTimeout =0 , WaitTimeSeconds = 0)
        
        if len(response["Messages"]) == 0:
            return None
        else:
            
            logger.debug("Message Received Successfully")

            message = response["Messages"][0]
            receiptHandle = message["ReceiptHandle"]
            
        # So now we have received the message
        # Now we need to purge this message from the MQ
        
        # Deleting message from MQ
        
        response = sqsClient.delete_message(QueueUrl = sqsUrl , ReceiptHandle = receiptHandle)
        
        return message
    except:
        return None

def lambda_handler(event, context):
    # TODO implement
    
   
    message = fetchMessageFromMQ()
    
    if message == None:
        logger.debug("No message found in the MQ")
        return 
    
    cuisine = message["MessageAttributes"]["CuisineType"]["StringValue"]
    location = message["MessageAttributes"]["Location"]["StringValue"]
    date = message["MessageAttributes"]["DiningDate"]["StringValue"]
    time = message["MessageAttributes"]["DiningTime"]["StringValue"]
    numOfPeople = message["MessageAttributes"]["People"]["StringValue"]
    email = message["MessageAttributes"]["Email"]["StringValue"]
    sessionID = message["MessageAttributes"]["sessionID"]["StringValue"]
    
    searchUrl = '''https://search-opensearch-bm76vifk5cwboacjwiduj6p6bm.us-east-1.es.amazonaws.com/restaurant/_search?q=$cuisine&size=500''' 
    headers = { "Content-Type": "application/json", "Authorization": "Basic bWFzdGVyOlJhbmRvbSMxMjM=" }

    template = Template(searchUrl)

    resp =  requests.get(template.substitute(cuisine=cuisine),headers=headers)
    

    logger.debug("Querying elastic Services for cuisine")
    respData = resp.json()['hits']['hits']
    print(respData)


    n = len(respData)
    indexes = []
    while len(indexes) != 5:
        ele = random.randint(0,n+1)
        if ele not in indexes:
            indexes.append(ele)

    resId =  [ele['_source']['RestaurantID'] for ele in respData]

    details =[]

    dbClient =  boto3.client('dynamodb')

    logger.debug("Fetching Restaurant details from Dynamo DB")

    for id in resId:
        response = dbClient.get_item(TableName='yelp-restaurants',Key={'bid': {'S': id}})
        print(response)
        details.append(response['Item'])

    if not details:
        logger.debug("Restaurants not found")
    else:

        EmailBody = "Based on your preferences, I recommend the following "+ cuisine +" restaurants for a group of "+ numOfPeople +" people, on "+ date+ " at "+ time + "\n"

        for i in range(3):
            dispAddress = []
            dispAddrList = details[i]["address"]["M"]["display_address"]["L"]
            for item in dispAddrList:
                dispAddress.append(list(item.values())[0])
            
            temp = str(i+1) + "."+ details[i]["name"]['S'] + " located at " + ','.join(dispAddress) 
            EmailBody = EmailBody + temp +"\n"
        
        EmailBody = EmailBody + 'Enjoy your Meal! \U0001F600'        
        
        print("Email Body prepared")
        # Before sending the mail we need to save the sessionId and emailBody in dynamo db
        dbResource =  boto3.resource('dynamodb')
        sessionTable = dbResource.Table('sessionData')
        dbClient =  boto3.client('dynamodb')

        print("Putting the sessionData into DB")
        if sessionID != "testuser":
            
            # Checking if we already have an entry in Db
            sessionData = dbClient.get_item(TableName='sessionData',Key={'sessionID': {'S': sessionID}})
            
            sessionDetails = sessionData.get('Item',None)
            print("Session Data", sessionData)
            if sessionDetails:
                # Append to the entry
                messageStr = sessionDetails['content']['S']
                
                messageStr = messageStr + "^" + EmailBody
                
                sessionTable.put_item(
                                   Item={
                                        "sessionID":sessionID,
                                        "content": messageStr
                                    }
                               )
                
            
            else:
                # Create a New Entry
            
                sessionTable.put_item(
                                   Item={
                                        "sessionID":sessionID,
                                        "content": EmailBody
                                    }
                               )

        # Sending the email        
        print("Sending Email")
        sesClient = boto3.client('sesv2')
        response = sesClient.send_email(FromEmailAddress='undefeatablesuchit@gmail.com',
            FromEmailAddressIdentityArn='arn:aws:ses:us-east-1:626235363664:identity/undefeatablesuchit@gmail.com',
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Content={
                'Simple': {
                    'Subject': {
                        'Data': 'Dine Out recommendations from Online Dining Coincerage Service',
                    },
                    'Body': {
                        'Text': {
                            'Data': EmailBody,
                            
                        }
                }
                
            }}
            )





    
