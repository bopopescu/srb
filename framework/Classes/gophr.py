from Classes.AbstractService import Service
from Modules.data_converter import data_converter as converter
from Modules.network import networking as netw
from Modules.data_validator import Validator 
from BuiltInService import requests
import os
import time
import datetime
import json
import re

import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
paramlist = {}
responese =""

class gophr(Service):
	def root(self,paramlist):
		true=True
		false = False
		data={
			"/": {
				"get": true
			},
			"type": {
				"get": true
			},
			"status": {
				"get": true
			},
			"label":{
				"post":false
			},
			"pickup":{
				"post":true
			},
			"tracking":{
				"get":false
			}

		}
		return data

	def type(self,paramlist):
		print("type")
		true=True
		false=False
		data={"type": "pickup","postal": false,"pickup": true,"dropoff": false,"linehaul": false}
		return data

	def status(self,paramlist):
		date = datetime.datetime.now() + datetime.timedelta(days=1)
		# curdate = re.sub(r'\s.*','',str(date))
		timeformat = re.sub(r'\..*','',str(date))
		timeformat =  re.sub(r'\s','T',str(timeformat))
		paramlabel={}
		paramtraking={}
		parampickup={
		  "shipment_id": "",
		  "origin": {
		    "first_name": "Mister",
		    "last_name": " John",
		    "phone": "+44 20 9999 8964",
		    "street_number": "",
		    "street_name": "",
		    "line1": "1 Grape St, Covent Garden",
		    "city": "London",
		    "zipcode": "WC2H 8ED",
		    "country_code": "GB",
			"email":"mister.john@gmail.com"
		  },
		  "pickup": {
		    "pickup_date": timeformat
		  },
		  "destination": {
		    "first_name": "David",
		    "last_name": "Beckbeck",
		    "company": "",
		    "street_number": "",
		    "street_name": "",
		    "line1": "25 Crescent Way",
		    "zipcode": "SE4 1QL",
		    "city": "London",
		    "country": "",
		    "country_code": "GB",
		    "phone": "+44 20 9999 1111",
		    "email": "",
		    "latitude": 0,
		    "longitude": 0
		  },
		  "parcel": {
		    "length_in_cm": 10,
		    "width_in_cm":10,
		    "height_in_cm": 10,
		    "weight_in_grams": 200,
		    "number_of_pieces": 0
		  }
		}
		objfunction=["root","type","pickup"]
		instance = Validator()
		api_url_request = os.environ["API_DEVEVELOPER_URL"]
		result = instance.get_all_status("gophr",api_url_request,objfunction,paramlabel,parampickup,"",paramtraking,"")
		return result
			

	def pickup(self,userparamlist):
		url = os.environ["GOPHR_PICKUP_URL"]

		req_list=["origin/first_name","origin/last_name","origin/line1","origin/zipcode","origin/email","origin/phone","origin/country_code",
		"destination/first_name","destination/last_name","destination/line1","destination/zipcode"]
		instance = Validator()
		checkparamlist = instance.json_check_required(req_list, userparamlist)
		if checkparamlist["status"]:
			paramlist=userparamlist
			# reqEmpty=["origin/line2","destination/line2"]
			# paramlist = instance.jsonCheckEmpty(reqEmpty,userparamlist)
			paramlist["origin"]["name"]  = str(paramlist["origin"]["first_name"])+" "+str(paramlist["origin"]["last_name"])
			paramlist["destination"]["name"]  = str(paramlist["destination"]["first_name"])+" "+str(paramlist["destination"]["last_name"])
		else:
			responseErr = {"status": 400,"errors": [{"detail": str(checkparamlist["message"])}]}
			raise Exception(responseErr)

		data = {
			"api_key" : os.environ["GOPHR_API_KEY"],
			"external_id" : "return_id",
			"pickup_person_name" :paramlist["origin"]["name"],
			"pickup_address1" : paramlist["origin"]["line1"],
			"pickup_postcode" : paramlist["origin"]["zipcode"],
			"pickup_city" : paramlist["origin"]["city"],
			"pickup_country_code" : paramlist["origin"]["country_code"],
			"pickup_email" : paramlist["origin"]["email"],#"mister.john@gmail.com"
			"pickup_mobile_number" : paramlist["origin"]["phone"],
			"pickup_tips_how_to_find" : "Tips to find",
			"delivery_person_name" : paramlist["destination"]["name"],
			"delivery_address1" : paramlist["destination"]["line1"],
			"delivery_postcode" : paramlist["destination"]["zipcode"],
			"delivery_city" : paramlist["destination"]["city"],
			"delivery_country_code" : paramlist["destination"]["country_code"],
			"delivery_mobile_number" : paramlist["destination"]["phone"],
			"size_x" : paramlist["parcel"]["length_in_cm"],
			"size_y" : paramlist["parcel"]["width_in_cm"],
			"size_z" : paramlist["parcel"]["height_in_cm"],
			"weight" : paramlist["parcel"]["weight_in_grams"],
			"order_value" : "100",
			"earliest_pickup_time" : paramlist["pickup"]["pickup_date"],
			"pickup_deadline" : paramlist["pickup"]["pickup_date"]
		}


		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
		resp = requests.post(url=url, data=data, headers=headers)
		result = json.loads(resp.text)
		try:
			paramlist["pickup_id"]= result["data"]["job_id"]
			paramlist["shipment_details"]=paramlist["parcel"]
		except:
			return result
		del paramlist["parcel"]
		return paramlist

	def tracking(self,paramlist):
		print("tracking")
		tracking_id= str(paramlist) #"20161026-102544-af700b752a5dae25"
		url = os.environ["GOPHR_TRACKING_URL"] #''

		data = {
			"api_key" : os.environ["GOPHR_API_KEY"],
			"job_id" : tracking_id,
		}

		headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
		resp = requests.post(url=url, data=data, headers=headers)
		# return resp.text
		resp  = json.loads(resp.text)
		# final_data=[]
		dt =[{
			"status":resp["data"]["status"],
			"steps": [
				{
					"status": resp["data"]["status"],
					"location": ""
				}
			]
		}]
		return dt

	def pickupslots(self, paramlist):
		print ("pickupslots from gophr")
		date = datetime.datetime.now()
		alldays=[]
		for l in range(7):
			date += datetime.timedelta(days=1)
			if date.isoweekday()==6:
				date += datetime.timedelta(days=2)
				print ("saturday +2: "+str(date))
			elif date.isoweekday()==7:
				date += datetime.timedelta(days=1)
				print ("sunday +1: "+str(date))
			else:
				print ("no check")
			newdate=re.sub(r'\s.*',' ',str(date))
			fullstartdate1="10:00:00"
			fullstartdate2="12:00:00"
			fullstartdate3="14:00:00"
			fullstartdate4="16:00:00"
			fullstartdate5="18:00:00"
			data={
		        "date": str(newdate),
		        "timezone":False,
		        "slots": [
			        {
						"start_time": fullstartdate1,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate2,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate3,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate4,
				        "duration": "120",
				        "availability": -1
					},
					{
						"start_time": fullstartdate5,
				        "duration": "120",
				        "availability": -1
					}
				]
		    }

			alldays.append(data)
		return alldays