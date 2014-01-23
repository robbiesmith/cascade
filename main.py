import time
import urllib.request
import json
from xml.dom import minidom
import calendar
import ftplib
import io

def windFormat(windspeed,direction):
  
    if ( direction < 22.5 or direction > 337.5  ):
        direction = "N";
    elif ( direction < 67.5 ):
        direction = "NE";
    elif ( direction < 112.5 ):
        direction = "E";
    elif ( direction < 157.5 ):
        direction = "SE";
    elif ( direction < 202.5 ):
        direction = "S";
    elif ( direction < 247.5 ):
        direction = "SW";
    elif ( direction < 292.5 ):
        direction = "W";
    elif ( direction < 337.5 ):
        direction = "NW";
    
    return "{0:.0f} mph from {1}".format(windspeed, direction)

#ftpPassword = raw_input("Enter FTP password: ")

wunderkey = "9d0379aadbc4d2fa";
forecastkey = "df995b53b3e151f1ff78ff56c6815bad";
traffickey = "8c629dd7-e525-4846-adcc-682d55d892e8";

locations = [ {'latitude': '47.41', 'longitude': '-121.405833', 'trafficId': 11, 'onthesnowId': '466','name': 'Summit at Snoqualmie', 'logo': 'summit.gif', 'nwac': {'key':'OSOSNO', 'columns':{-2: 'Base', -3: '24 Hr Snow'} } },
     {'latitude': '46.935642', 'longitude': '-121.474807', 'trafficId': 5, 'onthesnowId': '124','name': 'Crystal Mountain', 'logo': 'crystal.jpg', 'nwac':  {'key':'OSOCMT', 'columns':{-1: 'Base', -2: '24 Hr Snow'} } },
     {'latitude': '47.745095', 'longitude': '-121.091065', 'trafficId': 10, 'onthesnowId': '427','name': 'Stevens Pass', 'logo': 'stevens.gif', 'nwac':  {'key':'OSOSTS', 'columns':{-2: 'Base', -3: '24 Hr Snow'} } },
     {'latitude': '48.862259', 'longitude': '-121.678397', 'trafficId': 6, 'onthesnowId': '266','name': 'Mt. Baker', 'logo': 'baker.gif', 'nwac':  {'key':'OSOMTB', 'columns':{-1: 'Base', -2: '24 Hr Snow'} } },
     {'latitude': '47.443647', 'longitude': '-121.427819', 'trafficId': 11, 'onthesnowId': '804','name': 'Alpental', 'logo': 'alpental.jpg', 'nwac':  {'key':'OSOALP', 'columns':{-2: 'Base', -3: '24 Hr Snow', -1: '24 Hr Snow at Top'} } },
     {'latitude': '46.638358', 'longitude': '-121.390135', 'trafficId': 12, 'onthesnowId': '494','name': 'White Pass', 'logo': 'whitepass.gif', 'nwac':  {'key':'OSOWPS', 'columns':{-1: 'Base'} } } ]

# my @locationList = ( ",,11,466,Summit at Snoqualmie,summit.gif", #snoqualmie
#             "46.935642,-121.,5,124,Crystal Mountain,crystal.jpg", #crystal
#             ",-121.,10,427,Stevens Pass,stevens.gif", #stevens
#             ",-121.,6,266,Mt. Baker,baker.gif", #baker
#             ",-121.,11,804,Alpental,alpental.jpg", #alpental
#             ",-121.,12,494,White Pass,whitepass.gif" #white
# );
    # locationString - latitude,longitude,traffic id, onethsnow id

sleep = 7200; #update the server every 120 minutes
    
while ( 1 ):
    output = []

    trafficURL = "http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson?AccessCode=" + traffickey;
    response = urllib.request.urlopen(trafficURL)
    traffic_json = json.loads( response.read().decode("utf-8") )
    response.close()
    
#     onthesnowURL = "http://www.onthesnow.com/washington/snow-rss.html";
#     print (onthesnowURL);
#     snowDom = minidom.parse(urllib.request.urlopen(onthesnowURL))


    for item in locations:
        print (item)
        # https://api.forecast.io/forecast/df995b53b3e151f1ff78ff56c6815bad/37.8267,-122.423
        # http://graphical.weather.gov/xml/rest.php
        # http://api.wunderground.com/api/9d0379aadbc4d2fa/forecast/q/98068.json
        name = item['name']
        logo = item['logo']

        forecastURL = "https://api.forecast.io/forecast/" + forecastkey + "/" + item['latitude'] + "," + item['longitude']
        response = urllib.request.urlopen(forecastURL)
        decoded_json = json.loads( response.read().decode("utf-8"))
        response.close()
        
        current_json = decoded_json["currently"]
        #print(current_json)
        weather = []
        wind = windFormat(current_json["windSpeed"],current_json["windBearing"])
        icon = "http://snowcascades.com/cascade/icons/" + current_json["icon"] + ".png"
        pubTime = time.strftime("%a, %b %d %I:%M %p", time.localtime(current_json["time"]) )
        current = [ {'icon': icon },
                    {
                     "header": "Current conditions",
                     "text": current_json["summary"]
                    },
                    {
                     "header": "Temperature",
                     "text": "%.0f F" % current_json["temperature"]
                    },
                    {
                     "header": "Wind",
                     "text": wind
                    },
                    {
                     "header": "Last Update",
                     "text": pubTime
                    }
                  ]
        weather.append(current)
        
        forecastDaily = decoded_json["daily"]["data"]
        for day in forecastDaily:
            wind = windFormat(day["windSpeed"],day["windBearing"])
            icon = "http://snowcascades.com/cascade/icons/" + day["icon"] + ".png"
            forecastTime = time.strftime("%a, %b %d", time.localtime(day["time"]) )

            dayOutput = [ {'icon': icon },
                    {
                     "header": forecastTime, # strftime("%a, %b %d", localtime($forecastItem->{"time"})),
                     "text": day["summary"]
                    },
                    {
                     "header": "High",
                     "text": "%.0f F" % day["temperatureMax"]
                    },
                    {
                     "header": "Low",
                     "text": "%.0f F" % day["temperatureMin"]
                    },
                    {
                     "header": "Wind",
                     "text": wind
                    }
                  ]
            weather.append(dayOutput)
            

        weatherHash = {
            "title": "Weather",
            "tabs" : weather
        }

        conditionsURL = "http://www.nwac.us/data/{}". format( item["nwac"]["key"] )
        print (conditionsURL)
        response = urllib.request.urlopen(conditionsURL)
        decoded_text = response.read().decode("utf-8")
        lines = decoded_text.splitlines()

        conditionsItems = []

        for line in reversed(lines) :
            words = line.strip().split()
            if len(words) > 10:
                columns = item["nwac"]["columns"]
                for key in columns:
                    conditionsRow = {
                        "header": columns[key],
                        "text" : "{} inches".format(words[key])
                    }
                    conditionsItems.append(conditionsRow)
                updateTimeString = "%02d %02d %04d" % (int(words[0]), int(words[1]), int(words[2]))
                updateTime = time.strptime(updateTimeString, "%m %d %H%M")
                updateTimeRow = {
                    "header": "Last update",
                    "text" : time.strftime("%a, %b %d %I:%M %p", updateTime )
                }
                conditionsItems.append(updateTimeRow)
                break
        conditionsHash = {
            "title": "Snow",
            "body" : conditionsItems
        }
        
        #http://www.myweather2.com/developer/weather.ashx?uac=wtSAzBFQ8t&uref=5e64ad40-849f-42d2-9663-90e2300bb5e9&output=json
        # http://www.nwac.us/data/OSOSNO - snoqualmie
        # http://www.nwac.us/data/OSOMTB - baker
        # http://www.nwac.us/data/OSOCMT - crystal
        # http://www.nwac.us/data/OSOWPS - white
        # http://www.nwac.us/data/OSOALP - alpental
        # http://www.nwac.us/data/OSOSTS - stevens

        for pass_json in traffic_json:
            passId = pass_json["MountainPassId"]
            if ( passId == item["trafficId"] ):
                body = [
                    {
                     "header": pass_json["MountainPassName"],
                     "text": pass_json["RoadCondition"]
                    },
                    {
                     "header": pass_json["RestrictionOne"]["TravelDirection"],
                     "text": pass_json["RestrictionOne"]["RestrictionText"]
                    },
                    {
                     "header": pass_json["RestrictionTwo"]["TravelDirection"],
                     "text": pass_json["RestrictionTwo"]["RestrictionText"]
                    }
                ]
                

                trafficHash = {
                    "title": "Roads",
                    "body" : body
                }
                json.dumps(trafficHash)

                break

        resortComplete = {
            'name' : name,
            'logo': "http://snowcascades.com/cascade/icons/{}".format( logo ),
            'conditions': conditionsHash,
            'traffic': trafficHash,
            'weather': weatherHash
        }
        output.append(resortComplete)

    body = [
                {
                    "header": "Weather",
                    "text": "Weather data courtesy Forecast.io. Used by permission.",
                    "linktext": "Forecast.io",
                    "link": "http://www.forecast.io"
                 },
                {
                    "header": "Traffic",
                    "text": "Pass traffic data courtesy Washington State Department of Transportation. Used by permission."
                },
                {
                    "header" : "Snow",
                    "text" : "Snow conditions data courtesy Northwest Avalanche Center. Used by permission.",
                    "linktext" : "NWAC",
                    "link" : "http://www.nwac.us/"
                }
            ]
    more = (
                {
                    "header" : "Developed by",
                    "text" : "Rob Smith"
                 },
                {
                    "header" : "Get the app",
                    "text" : "SnowCascades is now available for iPhone and iPad. Find it on the App Store."
                 },
                {
                    "header" : "Check us out",
                    "text" : "Look for SnowCascades on Facebook and Twitter."
                }
            );

    dataHash = {
        "title" : "Data",
        "body" : body
    }

    moreHash = {
        "title" : "More",
        "body" : more
    }

    about = {
        'name' : 'About',
        'logo' : "http://snowcascades.com/cascade/icons/Snowflake-icon.png",
        'conditions' : dataHash,
        'traffic' : moreHash
    }

    output.append(about)

    json_text = json.dumps({"resorts":output})
    print(json_text)

    session = ftplib.FTP('ftp.talismith.com','robtali','foobat')
    session.cwd("/public_html/cascade")

    session.storlines( "STOR data.json", io.BytesIO(json_text.encode("utf-8")) )

    session.quit()

    break # do not loop - for dev

    time.sleep( sleep );