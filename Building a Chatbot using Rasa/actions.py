from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet, AllSlotsReset, Restarted
import zomatopy
import requests
import json
from soundex import get_soundex
from flask_mail import Mail, Message


def zomato_resto_res(lat,lon,cuisines,price,resturents=list(),offset=0):
	url = "https://developers.zomato.com/api/v2.1/search"
	querystring = { 
					"count":"100",
					"lat":str(lat),
					"lon":str(lon),
					"cuisines":str(cuisines),
					"sort":"rating",
					"order":"desc",
					"start":str(offset)}
	headers = {
    'Content-Type': "application/json",
	"user-key":"a06846e0cd54653319046326c4464f42"
    }
	response = requests.request("GET", url,  headers=headers, params=querystring)
	res=json.loads(response.text)
	res_resto=res['restaurants']
	for resto in res_resto:
		average_cost_for_two=resto['restaurant']['average_cost_for_two']
		if len(price) == 1:
			if average_cost_for_two >= price[0]:
				name=resto.get('restaurant').get('name')
				address=resto.get('restaurant').get('location').get('address')
				aggregate_rating=resto.get('restaurant').get('user_rating').get('aggregate_rating')
				resturents.append([name,address,aggregate_rating])
		else:
			if average_cost_for_two >= price[0] and average_cost_for_two <= price[1]:
				name=resto.get('restaurant').get('name')
				address=resto.get('restaurant').get('location').get('address')
				aggregate_rating=resto.get('restaurant').get('user_rating').get('aggregate_rating')
				resturents.append([name,address,aggregate_rating])
	if len(resturents) >= 10:
		return resturents[:10]
	else:
		offset=offset+100
		return zomato_resto_res(lat,lon,cuisines,price,resturents,offset)


class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"a06846e0cd54653319046326c4464f42"}
		zomato = zomatopy.initialize_app(config)

		#get location
		loc = tracker.get_slot('location')
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
		#get cuisine
		cuisine = tracker.get_slot('cuisine')
		cuisines_dict={'American': 1, 'Chinese': 25, 'Italian': 55 ,'Mexican': 73, 'North Indian': 50, 'South Indian': 85}
		
		#get price
		price = tracker.get_slot('price')

		results=zomato_resto_res(lat,lon,str(cuisines_dict.get(cuisine)),price)

		response=""
		noresults=False

		if len(results) == 0:
			response= "no results"
			noresults=True
		else:
			for restaurant in results[:5]:
				response=response+ "Found "+ restaurant[0]+ " in "+ restaurant[1]+" has been rated "+restaurant[2]+"\n"
		
		dispatcher.utter_message("-----"+response)
		return [SlotSet('noresults',noresults),SlotSet('location',loc),SlotSet('restaurants',results)]



class ActionSearchCity(Action):
	def name(self):
		return 'action_city'
	def run(self, dispatcher, tracker, domain):
		cities=json.load(open('./data/cities.json'))
		all_cities= cities['tire1'] + cities['tire2']
		
		cities_soundex={get_soundex(x.lower()):x for x in all_cities}

		changed_cities=json.load(open('./data/city_name_changed.json'))

		for index,i in enumerate(changed_cities):
			if i['new'] in all_cities:
				i['soundex']=get_soundex(i['old'])
				changed_cities[index]=i

		loc=tracker.get_slot('location')
		loc_soundex=get_soundex(loc)
		val=False
		if loc_soundex in cities_soundex.keys():
			val=True
			loc=cities_soundex[loc_soundex]
		else:
			for i in changed_cities:
				if 'soundex' in i and i['soundex'] == loc_soundex:
					val=True
					loc=i['new']
					break
		return [SlotSet('location',loc),SlotSet('location_type',val)]

class ActionGetCuisineSlection(Action):
	def name(self):
		return 'action_get_cuisine'
	
	def run(self,dispatcher,tracker,domain):
		val=tracker.get_slot('num')
		cuisines=['Chinese','Mexican','Italian','American','South Indian','North Indian']
		
		return [SlotSet('cuisine',cuisines[int(val)-1])]


class ActionGetPriceSelection(Action):
	def name(self):
		return 'action_get_price'
	
	def run(self,dispatcher,tracker,domain):
		val=tracker.get_slot('num')
		temp_dict={'1':[0,300],'2':[300,700],'3':[700]}
		
		return [SlotSet('price',temp_dict[str(val)])]




class ActionMailSend(Action):
	def name(self):
		return 'action_mail_send'
	
	def run(self,dispatcher,tracker,domain):
		email=tracker.get_slot('mail')
		location=tracker.get_slot('location')
		mail_success=True
		app = Flask(__name__)
		app.config.update(
			DEBUG=True,
			#EMAIL SETTINGS
			MAIL_SERVER='smtp.gmail.com',
			MAIL_PORT=465,
			MAIL_USE_SSL=True,
			MAIL_USERNAME = 'chatbotapp0002@gmail.com',
			MAIL_PASSWORD = 'Chat@123'
			)
		mail = Mail(app)

		try:
			msg_body=""
			restaurants=tracker.get_slot('restaurants')
			for res in restaurants:
				msg_body=msg_body+ "Found "+ res[0]+ " in "+ res[1]+" has been rated "+res[2]+"\n"
			
			msg = Message("Resturent lists in "+str(location),
		  		sender="chatbotapp0002@gmail.com",
		  		recipients=[email])
			msg.body = msg_body          
			mail.send(msg)
		except Exception as e:
			dispatcher.utter_message(str(e))
			mail_success=False
		
		return [SlotSet('mail_success',mail_success)]


class ActionResetSlots(Action):
	def name(self):
		return 'action_reset'
		
	def run(self, dispatcher, tracker, domain):
		#AllSlotsReset()
		return [AllSlotsReset()]

class ActionRestarted(Action): 	
    def name(self): 		
        return 'action_restarted' 	
    def run(self, dispatcher, tracker, domain): 
        return[Restarted()] 