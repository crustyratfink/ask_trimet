# ask_trimet
An Alexa skill to ask Portland's Tri-met about bus arrivals as you run out of the house, late for work. It requires that you have an AWS account, some knowledge of AWS Lambda, a Tri-met developer account, and a little Python mojo.

##How it works in action:

You say:
`Alexa, ask Tri-met to add stop ID 123`

And she adds it to DynamoDB. You can add all the stops near you.

(You can also say: `Alexa, ask Tri-met to remove stop ID 123` to remove it.)

Finally, when you're ready to go hop on a bus, you say:
`Alexa, ask Tri-met when the next bus arrives`

or, alternatively,
`Alexa, ask Tri-met when the next bus arrives at 123` if you're interested in a station other than your standard list.

And, ideally, she'll read back a list of arrivals with the bus number and stop ID. Fingers crossed.

_Note: this part's not done. Right now, I had to set up the DynamoDB key manually. On my [todo list](#todo)._

##Set up:

###application.cfg

Create a file in your root with the following contents:

```
APP_ID = <your trimet app id>
AWS_ACCESS_KEY = <your aws access credential>
AWS_SECRET_KEY = <your aws secret key>
AWS_REGION = <probably just us-east-1...>
```

###zappa_settings.json
This has an S3 bucket name in it. Change that. That one's MINE!

###Virtualenv
You'll want to set up a python virtual env, install the requirements, and use [zappa](https://github.com/Miserlou/Zappa) to deploy everything to Lambda. Something like this:

```
% virtualenv env
% source env/bin/activate
% pip install -r requirements.txt
% pip install zappa
% <edit the zappa settings file to put in your S3 bucket>
% zappa prod deploy
```

<a name="todo"></a>
##TODO


- Fix up the code so it doesn't look like I wrote it in the middle of the night like I did. I copy-pasta'd a lot of stuff in there. 
- Exception handling
- Take care of the initialization of the DynamoDB database with the user's userId (from the Alexa request). The boto3 library is a hot mess when it comes to DynamoDB. Or maybe that's just DynamoDB.
- I haven't figured a way to get the location of the device. That'd be cool. 
- So much more!

## Notes

A query to the Tri-met API looks like:

```https://developer.trimet.org/ws/V1/arrivals?locIDs=785&appID=<app id>&json=true```


Response:

~~~json
{
    resultSet: {
        arrival: [{
            departed: true,
            scheduled: "2016-09-30T12:00:15.000-0700",
            shortSign: "20 Beaverton TC",
            blockPosition: {
                feet: 7630,
                at: "2016-09-30T12:00:42.000-0700",
                trip: [{
                    route: 20,
                    destDist: 68586,
                    tripNum: 6729787,
                    pattern: 1,
                    progress: 60956,
                    dir: 0,
                    desc: "Beaverton TC"
                }],
                lng: -122.5803947,
                heading: 271,
                lat: 45.5227802
            },
            estimated: "2016-09-30T12:06:55.000-0700",
            dir: 0,
            route: 20,
            detour: true,
            piece: "1",
            fullSign: "20 Burnside/Stark to Beaverton TC via Portland City Center",
            block: 2070,
            locid: 785,
            status: "estimated"
        }, {
            departed: true,
            scheduled: "2016-09-30T12:20:15.000-0700",
            shortSign: "20 To NW 23rd Ave",
            blockPosition: {
                feet: 26734,
                at: "2016-09-30T12:00:47.000-0700",
                trip: [{
                    route: 20,
                    destDist: 68586,
                    tripNum: 6729788,
                    pattern: 11,
                    progress: 41852,
                    dir: 0,
                    desc: "West Burnside & Osage St"
                }],
                lng: -122.510608,
                heading: 269,
                lat: 45.5191456
            },
            estimated: "2016-09-30T12:24:13.000-0700",
            dir: 0,
            route: 20,
            detour: true,
            piece: "1",
            fullSign: "20 Burnside/Stark to 23rd Ave to Tichner",
            block: 2037,
            locid: 785,
            status: "estimated"
        }],
        queryTime: "2016-09-30T12:00:54.693-0700",
        location: [{
            lng: -122.610057408895,
            dir: "Westbound",
            lat: 45.5229580841898,
            locid: 785,
            desc: "E Burnside & NE 52nd"
        }]
    }
}

~~~

My Alexa **intent schema**:

~~~json
{
    "intents": [{
        "intent": "GetArrivals",
        "slots": [{
            "name": "location",
            "type": "AMAZON.NUMBER"
        }]
    },{
      "intent": "AddStopId",
      	"slots": [{
        	"name": "location",
          	"type": "AMAZON.NUMBER"
      }]
    },{
      "intent": "RemoveStopId",
      	"slots": [{
        	"name": "location",
          	"type": "AMAZON.NUMBER"
      }]
    },{
        "intent": "ListStopIds"
    }]
}
~~~

Sample utterances:

~~~
GetArrivals when the next buses are arriving at {location}
GetArrivals when does the bus come to {location}
GetArrivals when the next bus arrives at {location}
GetArrivals when busses arrive at {location}
GetArrivals for times at {location}
AddStopId to add stop i d {location}
RemoveStopId to remove stop i d {location}
ListStopIds what i d's I've stored
ListStopIds what my stops are
ListStopIds to list my stops
~~~