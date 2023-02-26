# Chatbot Dining Concierge #
Built by Team Members: 
Name: Suchit Sahoo, UNI: ss6630
Name: Prahlad Koratamaddi, UNI: pk2743

## S3 Front-end URL ##
[S3 Front-end URL](https://s3.amazonaws.com/static.chatbot/cloud-hw1-starter/chat.html)

## About ##
This is the final submission repository to satisfy the requirements of Assignment 1 in Cloud Computing and Big Data, taught by Prof. Sambit Sahu in Spring 2023 at Columbia University in the City of New York.

### Directory Structure: ###
1. All front-end code files are in the cloud-hw1-starter folder, in the same way as originally provided.
2. LF0.py, LF1.py and LF2.py are the lambda functions which are in the cloud-hw1-starter folder.
3. "AI Customer Service API-testProd-swagger.yaml" file in the cloud-hw1-starter folder is the YAML file generated through API Gateway.
4. "YelpScraper.py" in the cloud-hw1-starter folder is the Yelp Scraper script.

## Extra Credit Workflow ##
We use the browser's session ID to identify a user's conversation and store the session ID and corresponding recommendations in DynamoDB. 

In LF0, once the user prompts the GreetingIntent in Lex, we will check if the session ID associated with the request exists in the DB, and if it does, we will automatically serve up their previous recommendations. 
Otherwise, else we will continue with the normal workflow. 

The saving of session ID and recommendations to DynamoDB is done in LF2. 
The data model would have the key as the session ID, and the value as an array of recommendations.
In this design, we did not have the need to use an extra lambda function.

## Usage ##

1. Clone the repository.
2. Replace `/assets/js/sdk/apigClient.js` with your own SDK file from API
   Gateway.
3. Open `chat.html` in any browser.
4. Start sending messages to test the chatbot interaction.

