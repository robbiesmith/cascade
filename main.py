import time
import urllib.request
import json
from xml.dom import minidom
import calendar
import ftplib
import io
import getpass
import logging
import html2text

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

logger = logging.getLogger(__name__)

handler = logging.FileHandler('error_log.txt')
logger.addHandler(handler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

ftpPassword = getpass.getpass( "Enter FTP password: " )

wunderkey = "9d0379aadbc4d2fa";
forecastkey = "df995b53b3e151f1ff78ff56c6815bad";
traffickey = "8c629dd7-e525-4846-adcc-682d55d892e8";

locations = [ {'latitude': '47.41', 'longitude': '-121.405833', 'trafficId': 11, 'onthesnowId': '466','name': 'Summit at Snoqualmie', 'shortName': 'Summit', 'logo': 'summit.gif', 'nwac': {'key':'OSOSNO', 'columns':{-2: 'Base', -3: '24 Hr Snow'} } },
     {'latitude': '46.935642', 'longitude': '-121.474807', 'trafficId': 5, 'onthesnowId': '124','name': 'Crystal Mountain', 'shortName': 'Crystal', 'logo': 'crystal.jpg', 'nwac':  {'key':'OSOCMT', 'columns':{-1: 'Base', -2: '24 Hr Snow'} } },
     {'latitude': '47.745095', 'longitude': '-121.091065', 'trafficId': 10, 'onthesnowId': '427','name': 'Stevens Pass', 'shortName': 'Stevens', 'logo': 'stevens.gif', 'nwac':  {'key':'OSOSTS', 'columns':{-2: 'Base', -3: '24 Hr Snow'} } },
     {'latitude': '48.862259', 'longitude': '-121.678397', 'trafficId': 6, 'onthesnowId': '266','name': 'Mt. Baker', 'shortName': 'Mt. Baker', 'logo': 'baker.gif', 'nwac':  {'key':'OSOMTB', 'columns':{-1: 'Base', -2: '24 Hr Snow'} } },
     {'latitude': '47.443647', 'longitude': '-121.427819', 'trafficId': 11, 'onthesnowId': '804','name': 'Alpental', 'shortName': 'Alpental', 'logo': 'alpental.jpg', 'nwac':  {'key':'OSOALP', 'columns':{-2: 'Base', -3: '24 Hr Snow'} } }, # , -1: '24 Hr Snow at Top' is unreliable
     {'latitude': '46.638358', 'longitude': '-121.390135', 'trafficId': 12, 'onthesnowId': '494','name': 'White Pass', 'shortName': 'White Pass', 'logo': 'whitepass.gif', 'nwac':  {'key':'OSOWPS', 'columns':{-1: 'Base'} } } ]

backcountryLocations = [ {'label': 'Snoqualmie', 'key': 'cascade-west-snoqualmie-pass'},
                        {'label': 'Stevens', 'key': 'cascade-west-stevens-pass'},
                        {'label': 'White', 'key': 'cascade-west-white-pass'} ];

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

    try:
        trafficURL = "http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson?AccessCode=" + traffickey;
        response = urllib.request.urlopen(trafficURL)
        traffic_json = json.loads( response.read().decode("utf-8") )
        response.close()
    except:
        traffic_json = []
        logger.error('traffic server not responding', exc_info=True)
    
    try:
        onthesnowURL = "http://www.onthesnow.com/washington/snow-rss.html";
        snowDom = minidom.parse(urllib.request.urlopen(onthesnowURL))
    except:
        snowDom = minidom.Document()
        logger.error('onTheSnow not responding', exc_info=True)

    for item in locations:
        # https://api.forecast.io/forecast/df995b53b3e151f1ff78ff56c6815bad/37.8267,-122.423
        # http://graphical.weather.gov/xml/rest.php
        # http://api.wunderground.com/api/9d0379aadbc4d2fa/forecast/q/98068.json
        name = item['name']
        shortName = item['shortName']
        logo = item['logo']
        resortComplete = {
            'name' : name,
            'shortName' : shortName,
            'logo': "http://snowcascades.com/cascade/icons/{}".format( logo )
        }

        try:
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
            resortComplete['weather'] = weatherHash
        except:
            logger.error('forecast.io not responding or bad data', exc_info=True)

        try:
            conditionsURL = "http://www.nwac.us/data/{}". format( item["nwac"]["key"] )
            response = urllib.request.urlopen(conditionsURL)
            decoded_text = response.read().decode("utf-8")
            lines = decoded_text.splitlines()
        except:
            print("NWAC not responding")
            lines = []
            logger.error('NWAC not responding', exc_info=True)

        conditionsItems = []
        for node in snowDom.getElementsByTagName('item'):  
            if ( node.getElementsByTagName("ots:resort_id")[0].firstChild.nodeValue == item["onthesnowId"] ):
                conditionsRow = {
                    "header": "Status",
                    "text" : node.getElementsByTagName("ots:open_staus")[0].firstChild.nodeValue # [sic] - should be open_status
                }
                conditionsItems.append(conditionsRow)
                conditionsRow = {
                    "header": "Surface",
                    "text" : node.getElementsByTagName("ots:surface_condition")[0].firstChild.nodeValue
                }
                conditionsItems.append(conditionsRow)

#         foreach my $item (@{$data->{channel}->{item}}) {
#             if ( $item->{'ots:resort_id'} == $onthesnowId ) {

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
                updateTimeString = "{} %02d %02d %04d".format( time.strftime("%Y", time.localtime() ) ) % (int(words[0]), int(words[1]), int(words[2]))
                updateTime = time.strptime(updateTimeString, "%Y %m %d %H%M")
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
        resortComplete['conditions'] = conditionsHash
        
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
                resortComplete['traffic'] = trafficHash

                break

        output.append(resortComplete)

    snoqHash = {}
    stevensHash = {}
    whiteHash = {}
    for item in backcountryLocations:
        #http://www.nwac.us/api/v2/avalanche-region-forecast/?format=json&zone=cascade-west-snoqualmie-pass
        #http://www.nwac.us/static/images/danger-levels/moderate.png
        #http://www.nwac.us/static/common/images/nwac-logo-square.jpg
# "day1_danger_elev_high": "Moderate",
#             "day1_danger_elev_low": "Moderate",
#             "day1_danger_elev_middle": "Moderate",
#             "day1_date": "2014-02-27",
#             "day1_detailed_forecast": "<p>East winds should abate Wednesday night and temperatures should warm around the Snoqualmie Pass area Thursday. &nbsp;Partly sunny skies through mid-day will further help weaken the most recently formed ice crust and may allow wet-loose avalanches to become possible on&nbsp;steeper solar facing aspects.&nbsp;</p>\r\n\r\n<p>Human triggered large or very large avalanches have become unlikely but&nbsp;are still high consequence if able to step down to poorly bonded&nbsp;previous&nbsp;storm layers or buried persistent weak layers. Cornices have grown large and may be sensitive.&nbsp;A cornice failure could provide a large enough natural trigger to trigger a large and destructive avalanche. &nbsp;Avoid areas in avalanche terrain where you believe the snowpack to be shallower and potentially easier to trigger a deep PWL.&nbsp;</p>\r\n",
#             "day1_trend": null,
#             "day1_warning": "none",
#             "day1_warning_end": null,
#             "day1_warning_text": "",
#             "day2_danger_elev_high": "Moderate",
#             "day2_danger_elev_low": "Moderate",
#             "day2_danger_elev_middle": "Moderate",
#             "day2_trend": null,
#             "day2_warning": "none",
#             "day2_warning_end": null,
#             "day2_warning_text": "",
#             "id": 524,
#             "order": 3,
#             "publish_date": "2014-02-26T18:31:01",
#             "resource_uri": "/api/v2/avalanche-region-forecast/524/",
#             "snowpack_discussion": "<p>Deep recent storm snow after the weekend has been drastically changed in the Snoqualmie Pass area as of Tuesday morning.&nbsp;Early Monday morning a period of freezing rain occurred in the Snoqualmie Pass area depositing a thin crust. &nbsp;An additional 6 to 8 inches of new snow fell over that layer before a more widespread freezing rain event occurred overnight Monday. &nbsp;This has left a clear supportable ice layer capping deeper low density snow that fell earlier. &nbsp;</p>\r\n\r\n<p>While the current conditions do not support an avalanche danger, they do support a falling and sliding hazard as the surface in most areas is a smooth hard ice layer.</p>\r\n\r\n<p>There remains to be a concern for deep slab releases in this area, given the many recent large slides over the past week. &nbsp;However with the current ice structure it will likely take a significant trigger, such as a very large cornice collapse to possibly initiate a slide to that deep layer. &nbsp;Reports of a very large natural hard slab avalanche off steep north facing&nbsp;terrain of&nbsp;Chair Peak near Alpental&nbsp;partially caught 3 skiers Saturday. Luckily&nbsp;no on was injured in this potentially deadly&nbsp;avalanche with a&nbsp;10&#39; crown. &nbsp;It is believed this slide was initiated by a smaller slide or possible cornice failure then stepped down to the deep layer.&nbsp;This&nbsp;avalanche paired with the frequent and large results from ski patrol&nbsp;should steer&nbsp;the discussion to&nbsp;terrain management of&nbsp;low probability and high consequence slides that release down to old storm layers or the late Jan&nbsp;crust.</p>\r\n\r\n<p>Please see the other west slopes and Cascade Passes forecast for a more complete picture of the&nbsp;avalanche and snowpack conditions elsewhere.&nbsp;</p>\r\n",
        try:
            backcountryURL = "http://www.nwac.us/api/v2/avalanche-region-forecast/?format=json&zone={}". format( item["key"] )
            response = urllib.request.urlopen(backcountryURL)
            decoded_json = json.loads( response.read().decode("utf-8"))
            response.close()
        
            current_json = decoded_json["objects"][0]
            
            if item["label"] == 'Snoqualmie':
                activeItem = snoqHash
            elif item["label"] == 'Stevens':
                activeItem = stevensHash
            elif item["label"] == 'White':
                activeItem = whiteHash
            else:
                continue

            activeItem['title'] = item["label"]
            icon = "http://www.nwac.us/static/images/danger-levels/{}.png". format( current_json['day1_danger_elev_low'].lower() )
            activeItem['body'] = [
                                  {'icon': icon },
                                  {'header' : 'Avalanche danger level',
                                   'text' : current_json['day1_danger_elev_low']
                                  },
                                  {'header' : 'Details',
                                   'text' : html2text.html2text(current_json['day1_detailed_forecast']),
                                   'linktext' : 'More info',
                                   'link' : 'http://www.nwac.us/avalanche-forecast/current/{}/'. format( item["key"] )
                                  }
                                ]

        except:
            print("NWAC avalanche not responding")
            logger.error('NWAC avalanche not responding', exc_info=True)

    backcountry = {
        'name' : 'Backcountry',
        'shortName' : 'Backcountry',
        'logo' : "http://www.nwac.us/static/common/images/nwac-logo-square.jpg",
        'conditions' : snoqHash,
        'traffic' : stevensHash,
        'extra' : whiteHash
    }

    output.append(backcountry)

    body = [
                {
                    "header": "Weather",
                    "text": "Weather data courtesy Forecast.io. Used by permission.",
                    "linktext": "Forecast.io",
                    "link": "http://www.forecast.io"
                 },
                {
                    "header": "Roads",
                    "text": "Pass highway data courtesy Washington State Department of Transportation. Used by permission."
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
                    "text" : "SnowCascades is now available for iPhone and iPad. Find it on the App Store.",
                    "linktext" : "App Store",
                    "link" : "https://itunes.apple.com/us/app/snowcascades/id789974240"
                 },
                {
                    "header" : "Check us out",
                    "text" : "Look for SnowCascades on Facebook and Twitter.",
                    "linktext" : "On Twitter",
                    "link" : "https://twitter.com/SnowCascades"
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
        'shortName' : 'About',
        'logo' : "http://snowcascades.com/cascade/icons/Snowflake-icon.png",
        'conditions' : dataHash,
        'traffic' : moreHash
    }

    output.append(about)

    json_text = json.dumps({"resorts":output},indent=2)
    print(json_text)

    try:
        session = ftplib.FTP('ftp.talismith.com','robtali',ftpPassword)
        session.cwd("/public_html/cascade")
    
        session.storlines( "STOR data.json", io.BytesIO(json_text.encode("utf-8")) )
    
        session.quit()
    except:
        print("ftp upload failed")
        logger.error('ftp upload failed', exc_info=True)
        

    print (time.strftime("%a, %b %d %I:%M %p", time.localtime() ))

    # break # do not loop - for dev

    time.sleep( sleep );
