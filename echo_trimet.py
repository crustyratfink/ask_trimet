from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import requests
import json
from dateutil.relativedelta import *
from dateutil.parser import *
from datetime import *
import commands
import os
import random
import logging
import boto3

app = Flask(__name__)
app.config.from_pyfile('application.cfg', silent=False)
ask = Ask(app, '/')
names = ["buddy","dude","chum","my friend","Dave","putzy"]

def get_dynamo_client():
    return boto3.client(
        'dynamodb',
        aws_access_key_id=os.environment.get('aws_access_key'),
        aws_secret_access_key=os.environment.get('aws_secret_key'),
        region_name=os.environment.get('aws_region')
        )

@ask.intent('GetArrivals')
def arrivals(location):
    client = get_dynamo_client()
    stored_locations = client.get_item(TableName='stop_ids',
                Key={'user_id':{'S':session.user.userId}})
    if stored_locations.get("Item"):
        location = str(",".join(stored_locations["Item"]["stop_ids"]['NS']))
    if location==None or location=="home":
        location = "444,785"  
    url = "https://developer.trimet.org/ws/V1/arrivals?locIDs={}&appID={}&json=true".format(location,app.config["APP_ID"])
    try:
        api_response_json = requests.get(url)
        api_response = json.loads(api_response_json.text)
        now = parse(commands.getoutput("date"))
        alexa_response = ""
        if "resultSet" in api_response and "arrival" in api_response["resultSet"]:
            for arrival in api_response["resultSet"]["arrival"]:
                arrival_time = 0
                if arrival.get("status")=="scheduled": 
                    arrival_time = parse(arrival["scheduled"])
                else:
                    arrival_time = parse(arrival["estimated"])
                route = arrival["route"]
                delta = relativedelta(arrival_time, now).minutes
                if alexa_response=="":
                    alexa_response = "The next {} bus will arrive at {} in ".format(str(route),str(arrival["locid"]))
                else:
                    alexa_response += ". A {} bus will arrive at {} in ".format(str(route),str(arrival["locid"]))
                alexa_response += "{} minutes".format(str(delta))
        else:
            alexa_response="Sorry, I couldn't find any arrival times for you".format(random.choice(names))
    except Exception as e:
        alexa_response="I'm sorry, {}, something went horribly wrong. {}".format(random.choice(names),e)
    return statement(alexa_response)

@ask.intent('AddStopId')
def add_stop_id(location):
    client = get_dynamo_client()
    result = client.get_item(TableName='stop_ids',
                Key={'user_id':{'S':session.user.userId}})
    if result['ResponseMetadata']['HTTPStatusCode'] == 404:
        return statement("Your ID was not found.")
    else:
        alexa_response="Okeedoke. Adding stop ID {}".format(location)
        result = client.update_item(
            TableName='stop_ids',
            Key={
                'user_id': {'S':session.user.userId}
            },
            UpdateExpression='ADD stop_ids :i',
            ExpressionAttributeValues={
                ":i": {'NS':[location]}
            },
            ReturnValues="UPDATED_NEW"
        )
        # if result['ResponseMetadata']['HTTPStatusCode'] == 200 and result["Item"]:
        return statement(alexa_response)

@ask.intent('RemoveStopId')
def remove_stop_id(location):
    client = get_dynamo_client()
    result = client.get_item(TableName='stop_ids',
                Key={'user_id':{'S':session.user.userId}})
    if result['ResponseMetadata']['HTTPStatusCode'] == 404:
        return statement("Your ID was not found.")
    else:
        alexa_response="Okeedoke. Removing stop ID {}".format(location)
        result = client.update_item(
            TableName='stop_ids',
            Key={
                'user_id': {'S':session.user.userId}
            },
            UpdateExpression='DELETE stop_ids :i',
            ExpressionAttributeValues={
                ":i": {'NS':[location]}
            },
            ReturnValues="UPDATED_NEW"
        )
        # if result['ResponseMetadata']['HTTPStatusCode'] == 200 and result["Item"]:
        return statement(alexa_response)

@ask.intent('ListStopIds')
def list_stop_ids():
    alexa_response=""
    client = get_dynamo_client()
    stored_locations = client.get_item(TableName='stop_ids',
                Key={'user_id':{'S':session.user.userId}})
    if stored_locations.get("Item"):
        alexa_response = "You've stored stop i d's {}".format(str(" and ".join(stored_locations["Item"]["stop_ids"]['NS'])))
    else:
        alexa_response = "Sorry, {}, you haven't stored any stop i d's".format(random.choice(names))
    return statement(alexa_response)

if __name__ == "__main__":
	app.run(debug=True)
