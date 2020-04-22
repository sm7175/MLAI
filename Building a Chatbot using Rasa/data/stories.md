## story1
* greet
    - utter_greet
* restaurant_search
    - utter_ask_location
* restaurant_search{"location": "delhi"}
    - slot{"location": "delhi"}
	- action_city
    - slot{"location_type": true}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "chinese"}
    - slot{"num": 1}
    - action_get_cuisine
    - slot{"cuisine": "chinese"}
	- utter_ask_price
* restaurant_search{"price": ["more","300"]}
    - slot{"num": 2}
    - action_get_price
    - slot{"price":[300,700]}
    - action_restaurant
	- slot{"noresults": false}
    - utter_ask_ifmail
* affirm
    - utter_ask_mail
    - slot{"mail": "sm7175@gmail.com"}
    - action_mail_send
    - slot{"mail_success": true}
    - utter_email_Sent
* goodbye
    - utter_goodbye
    - action_reset
	- action_restarted


