#!/usr/bin/env perl
use strict;
use warnings;

use LWP;
use XML::Simple;
use URI::Escape;
use POSIX qw(strftime);
use Date::Parse;
use JSON qw( decode_json encode_json );
use Data::Dumper;
use Path::Class;
use Net::FTP;

print "Enter FTP password: ";
chomp( my $ftpPassword = <> );

# Create a user agent object
#  use LWP::UserAgent;
my $ua = LWP::UserAgent->new(ssl_opts => { verify_hostname => 0 });

#Create the xml parser
my $xml = new XML::Simple;

my $wunderkey = "9d0379aadbc4d2fa";
my $forecastkey = "df995b53b3e151f1ff78ff56c6815bad";
my $traffickey = "8c629dd7-e525-4846-adcc-682d55d892e8";

my @locationList = ( "47.41,-121.405833,11,466", #snoqualmie
			"46.935642,-121.474807,5,124", #crystal
			"47.745095,-121.091065,10,427", #stevens
			"48.862259,-121.678397,6,266", #baker
			"47.443647,-121.427819,11,804", #alpental
			"46.638358,-121.390135,12,494" #white
);
	# locationString - latitude,longitude,traffic id, onethsnow id

my $sleep = 1; #first time through run right away
	
while ( sleep( $sleep ) ) {
	$sleep = 1200;

	my $now_string = localtime;

	print "$now_string\n";
	my @output;
	
	foreach my $locationString (@locationList) {
		my @locationInfo = split(',',$locationString);
		
		my $latitude = $locationInfo[0];
		my $longitude = $locationInfo[1];
		my $trafficId = $locationInfo[2];
		my $onthesnowId = $locationInfo[3];
	
		# https://api.forecast.io/forecast/df995b53b3e151f1ff78ff56c6815bad/37.8267,-122.423
		# http://graphical.weather.gov/xml/rest.php
		# http://api.wunderground.com/api/9d0379aadbc4d2fa/forecast/q/98068.json
		my $forecastURL = "https://api.forecast.io/forecast/${forecastkey}/${latitude},${longitude}";
		my $forecastReq = HTTP::Request->new(GET => $forecastURL);
		print "${forecastURL}\n";
		my $res = $ua->request($forecastReq);
	
		my %weatherHash;
		
	  	if ($res->is_success) {
			my $decoded_json = decode_json( $res->content );
			my $forecastJson = $decoded_json->{"daily"}->{"data"};
			my @weather;
	    	for my $forecastItem (@$forecastJson) {
	    		my $forecastTime = strftime("%a, %e %b %Y %H:%M:%S %z", localtime($forecastItem->{"time"}));
	    		my @day = (
		    		{
		    			"header" => strftime("%A", localtime($forecastItem->{"time"})),
		    			"text" => $forecastItem->{"summary"}	    			
		    		},
		    		{
		    			"header" => "High",
		    			"text" => $forecastItem->{"temperatureMax"}	    			
		    		},
		    		{
		    			"header" => "Low",
		    			"text" => $forecastItem->{"temperatureMin"}	    			
		    		},
		    		{
		    			"header" => "Wind",
		    			"text" => $forecastItem->{"windSpeed"} . " from " . $forecastItem->{"windBearing"}  			
		    		}
	    		);
#	    		my %dayHash = (
#			        'date'=> $forecastTime,
#			        'icon'=> $forecastItem->{"icon"},
#			        'min'=> $forecastItem->{"temperatureMin"},
#			        'max'=> $forecastItem->{"temperatureMax"},
#			        'wind'=> $forecastItem->{"windSpeed"},
#			        'windBearing'=> $forecastItem->{"windBearing"},
#			        'visibility'=> $forecastItem->{"visibility"},
#			        'text'=> $forecastItem->{"summary"}
#			    );
			    push(@weather, \@day);
			}
			%weatherHash = (
				"title" => "Weather",
				"tabs" => \@weather
			)
	  	}
	               
	# the wunderground version
	#	my $forecastURL = "http://api.wunderground.com/api/${wunderkey}/forecast/q/98068.json";
	#	my $forecastReq = HTTP::Request->new(GET => $forecastURL);
	#	print "${forecastURL}\n";
	#	my $res = $ua->request($forecastReq);
	#
	#	my @weather;
	#	
	#  	if ($res->is_success) {
	#		my $decoded_json = decode_json( $res->content );
	#		my $forecastJson = $decoded_json->{"forecast"}->{"txt_forecast"};
	#		my $forecastDayJson = $forecastJson->{"forecastday"};
	#    	for my $forecastItem (@$forecastDayJson) {
	#    		my %dayHash = (
	#		        'period'=> $forecastItem->{"title"},
	#		        'text'=> $forecastItem->{"fcttext"}
	#		    );
	#		    push(@weather, \%dayHash);
	#		}
	#  	}
	
		# http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson?AccessCode={ACCESSCODE}
	
		my $trafficURL = "http://www.wsdot.wa.gov/Traffic/api/MountainPassConditions/MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson?AccessCode=${traffickey}";
		my $trafficReq = HTTP::Request->new(GET => $trafficURL);
		my $trafficRes = $ua->request($trafficReq);
		print "${trafficURL}\n";
		my %trafficHash = ();
		
	  	if ($trafficRes->is_success) {
			my $decoded_json = decode_json( $trafficRes->content );
	    	for my $passItem (@$decoded_json) {
				my $passId = $passItem->{"MountainPassId"};
				if ( $passId == $trafficId ) {
					my @directions = (
			    			{
			    				"direction" => $passItem->{"RestrictionOne"}->{"TravelDirection"},
			    				"text" => $passItem->{"RestrictionOne"}->{"RestrictionText"}
			    			},
			    			{
			    				"direction" => $passItem->{"RestrictionTwo"}->{"TravelDirection"},
			    				"text" => $passItem->{"RestrictionTwo"}->{"RestrictionText"}
			    			}
					);
					my @body = (
							{
				    			"header" => $passItem->{"MountainPassName"},
				    			"text" => $passItem->{"RoadCondition"}
							},
			    			{
				    			"header" => $passItem->{"RestrictionOne"}->{"TravelDirection"},
				    			"text" => $passItem->{"RestrictionOne"}->{"RestrictionText"}
			    			},
			    			{
				    			"header" => $passItem->{"RestrictionTwo"}->{"TravelDirection"},
				    			"text" => $passItem->{"RestrictionTwo"}->{"RestrictionText"}
			    			}
			    		);
		    		%trafficHash = (
		    			"title" => "Roads",
		    			"body" => \@body
		    		);
#		    		%trafficHash = (
#		    			'name' => $passItem->{"MountainPassName"},
#		    			'summary' => $passItem->{"RoadCondition"},
#		    			'weather' => $passItem->{"WeatherCondition"},
#		    			'temp' => $passItem->{"TemperatureInFahrenheit"},
#		    			'directions' => \@directions
#		    		);
				}
			}
	  	}
	
	# http://www.onthesnow.com/washington/snow-rss.html
	# http://www.onthesnow.com/ots/webservice_tools/OTSWebService2009.html
		my $onthesnowURL = "http://www.onthesnow.com/washington/snow-rss.html";
		my $onthesnowReq = HTTP::Request->new(GET => $onthesnowURL);
		my $onthesnowRes = $ua->request($onthesnowReq);
		print "${onthesnowURL}\n";
		my %conditionsHash = ();
		my $name;
	
	  	if ($onthesnowRes->is_success) {
			my $data = $xml->XMLin($onthesnowRes->content);
			foreach my $item (@{$data->{channel}->{item}}) {
				if ( $item->{'ots:resort_id'} == $onthesnowId ) {
#		    		%conditionsHash = (
#				        'date' => $item->{"pubDate"},
#				        'description' => $item->{"description"},
#				        'base' => $item->{"ots:base_depth"},
#				        'recent' => $item->{"ots:snowfall_48hr"},
#				        'surface' => $item->{"ots:surface_condition"},
#				        'metric' => $item->{"ots:base_depth_metric"},
#				        'status' => $item->{"ots:open_staus"}
#				    );
					my @body = (
							{
				    			"header" => "Status",
				    			"text" => $item->{"ots:open_staus"}
							},
			    			{
				    			"header" => "Base",
				    			"text" => $item->{"ots:base_depth"}
			    			},
			    			{
				    			"header" => "Last 48 hours",
				    			"text" => $item->{"ots:snowfall_48hr"}
			    			},
			    			{
				    			"header" => "Last update",
				    			"text" => $item->{"pubDate"}
							}
			    		);
					
		    		%conditionsHash = (
		    			"title" => "Conditions",
		    			"body" => \@body
		    		);
				    $name = $item->{"title"};
				}
			}
	  	}
		my %resortComplete = (
			'name' => $name,
	        'conditions' => \%conditionsHash,
	        'traffic' => \%trafficHash,
	        'weather' => \%weatherHash
	    );
		push(@output, \%resortComplete);
	}
	my $json_text = encode_json(\@output);
	print "$json_text\n";

	#http://perldoc.perl.org/Net/FTP.html
    my $ftp = Net::FTP->new("ftp.talismith.com", Debug => 0)
      or die "Cannot connect: $@";
    $ftp->login("robtali",$ftpPassword)
      or die "Cannot login: ", $ftp->message;
    $ftp->cwd("/public_html/cascade")
      or die "Cannot change working directory: ", $ftp->message;

	open(my $FH, "<", \$json_text)
		or die "Cannot open file handle";
	$ftp->put($FH, "data.json")
		or die "CAnnot write file: ", $ftp->message;

    $ftp->quit;
}

  
