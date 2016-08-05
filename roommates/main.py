#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Models
from person import Person
from home import Home
from sticky import Sticky
from chores import Chore
from bills import Bills


# Personal Libraries
import helpers
import login
import render
import logging
#import my_calendar



# Outside libraries
from google.appengine.api import users
from google.appengine.api import app_identity
import jinja2
import os
import time
import json
#import urllib
#import urllib2
import webapp2

from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.contrib.appengine import OAuth2Decorator
from googleapiclient.discovery import build
import datetime
from httplib2 import Http


# Initialize Jinja Environment
env = jinja2.Environment(loader= jinja2.FileSystemLoader('templates'))

decorator = OAuth2Decorator(
	client_id='270567588357-nnleha1dmgvgr7jatb1du51ruvqn4mou.apps.googleusercontent.com',
	client_secret='cAn4N7YIjckbjRaHWNqp1OEZ',
	scope='https://www.googleapis.com/auth/calendar')




service = build('calendar', 'v3')



class TestHandler(webapp2.RequestHandler):
	def get(self):
		helpers.createNewCal(self)




# Main Handler that either shows the login page, the create an account page, or the dashboard
class MainHandler(webapp2.RequestHandler):
	def get(self):
		# Get current google account that is signed in
		user = users.get_current_user()
		# Check if there is a user signed in
		if user:
			# Check if user has an account set up
			person = login.is_roommate_account_initialized(user) #Change to check if in home

			if person: 
				if login.is_in_room(self, person):
					helpers.redirect(self, '/dashboard', 0)
			# Otherwise, prompt user to create account
				else: 
					helpers.redirect(self, '/newJoinHome', 0) #/new_join_home
			else:
				#redirect to create account page
				helpers.redirect(self, '/newJoinHome', 0) #/new_join_home
		# If there is no user, prompt client to login
		else:
			login.render_login_page(self)


class CreateHomeHandler(webapp2.RequestHandler): #Change to redirect for /new_join_home
	def get(self):
		# Get current google account that is signed in
		user = users.get_current_user()
		# Check if there is a user signed in
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				if person.home_key:
					helpers.redirect(self, '/', 0)
			render.render_page_without_header(self, 'newJoinHome.html', 'Join a Room')
		# If there is no user, prompt client to login
		else:
			helpers.redirect(self, '/',0)
	@decorator.oauth_required
	def post(self):
		#retrieve data from form

		name=self.request.get('name_b')
		phone_number = int(self.request.get('phone_number1_b') + self.request.get('phone_number2_b') + self.request.get('phone_number3_b'))
		color = self.request.get('color')
		#create new person object
		user = users.get_current_user()

		person = Person(name=name, color=color, phone_number = phone_number, user_id = user.user_id(), email_address = user.email(), calendar_id=user.email())



		home_name = self.request.get('home_name_b')
		homes_with_same_name = Home.query().filter(Home.name == home_name).fetch()
		logging.info(self.request.get('password_a'))
		logging.info(self.request.get('password_b'))
		if len(homes_with_same_name) > 0: #If home with same name already exists
			data = {'error': 'This home name is already taken'}
			render.render_page_with_data_no_header(self, 'newJoinHome.html', 'Error: Home Name Taken', data)
		elif not (self.request.get('password_b') == self.request.get('password_a')):
			data = {'error' : 'Error: Passwords do not match'}
			render.render_page_with_data_no_header(self, 'newJoinHome.html', 'Join a Room', data)
		else:
			password = helpers.hashPass(self.request.get('password_b'))
			
			#Creates a calendar to be shared (on service account)
			calID = helpers.createNewCal(self, home_name)

			new_home = Home(name= home_name, password = password, calendar_id = calID, occupants = [user.user_id()])


			person.home_key = new_home.put()
			person.put()



			#Share calendar with user
			scopes = ['https://www.googleapis.com/auth/calendar']
			credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scopes=scopes)
			http_auth = credentials.authorize(Http())
			rule = {
				'scope': {
					'type': 'user',
					'value': user.email()
				},
				'role': 'reader'
			}

			created_rule = service.acl().insert(calendarId=calID, body=rule).execute(http=http_auth)




			logging.info(calID)

			#Update new calendar with events of person who just joined
			#Gets primary calendary ID
			http = decorator.http()
			#Call the service using the authorized Http object.
			now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
			requestResults = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute(http=http)
			
			for event in requestResults['items']:
				helpers.addEventToCal(self, event, calID)

				#redirect to create a calendar
			helpers.redirect(self, '/dashboard',1000)




class JoinHomeHandler(webapp2.RequestHandler):
	# def get(self): #NOT NEEDED ANYMORE, ONLY POST
	#     # Get current google account that is signed in
	#     user = users.get_current_user()
	#     # Check if there is a user signed in
	#     if user:
	#         person = login.is_roommate_account_initialized(user)
	#         if person:
	#             # Display create a Home page
	#             render.render_page_without_header(self, 'joinHome.html', 'Join a Home')
	#         else:
	#            helpers.redirect(self, '/',0)
	#     # If there is no user, prompt client to login
	#     else:
	#         helpers.redirect(self, '/',0)
	def get(self):
		helpers.redirect(self, '/dashboard',1000)

	@decorator.oauth_required
	def post(self):
		
		name = self.request.get('name')
		phone_number = int(self.request.get('phone_number1') + self.request.get('phone_number2') + self.request.get('phone_number3'))
		#create new person object
		user = users.get_current_user()


		color = self.request.get('color')
		person = Person(name=name, color=color, phone_number = phone_number, user_id = user.user_id(), email_address = user.email(), calendar_id=user.email())







		#retrieve data from form
		home_name = self.request.get('home_name')
		password = helpers.hashPass(self.request.get('password'))
		# Query for home object
		potential_home = Home.query().filter(Home.name == home_name, Home.password == password).fetch()
		if potential_home:
			potential_home[0].occupants.append(user.user_id())
			home_key = potential_home[0].put()
			person.put()
			person.home_key = home_key

			#Share Calendar
			calID = potential_home[0].calendar_id

			#Share calendar with user
			scopes = ['https://www.googleapis.com/auth/calendar']
			credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scopes=scopes)
			http_auth = credentials.authorize(Http())
			rule = {
				'scope': {
					'type': 'user',
					'value': user.email()
				},
				'role': 'reader'
			}

			created_rule = service.acl().insert(calendarId=calID, body=rule).execute(http=http_auth)



			logging.info(calID)

			#Update new calendar with events of person who just joined
			#Gets primary calendary ID
			http = decorator.http()
			#Call the service using the authorized Http object.
			now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
			requestResults = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute(http=http)
			
			for event in requestResults['items']:
				helpers.addEventToCal(self, event, calID)




			# requestResults = service.events().list(calendarId='primary', timeMin=now, singleEvents=True, orderBy='startTime').execute(http=http)
			
			# for event in requestResults['items']:
			# 	helpers.addEventToCal(self, event, calID)

			#DONE WITH PASTED CODE




			person.put()
			data = {'home_name': home_name}
			render.render_page_with_data(self, 'successfullyJoinedHome.html', 'Successfully Joined Home', data)
			helpers.redirect(self, '/dashboard', 1000)
		else:
			# REPORT to client to try again. wrong name or password
			data = {'error': 'You have entered an incorrect home name or password'}
			render.render_page_with_data_no_header(self, 'newJoinHome.html', 'Error: Wrong Name or Password', data)


		## TODO: redirect to create a calendar




class DashboardHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				render_data = helpers.getDashData(self, person)
				render.render_page_with_data(self, 'dashboard.html', person.name +"'s Dashboard", render_data)
			else:
			   helpers.redirect(self, '/', 0) 
		else:
			helpers.redirect(self, '/', 0)



class CreateStickyHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				render.render_page(self, 'createSticky.html', "Create a Sticky")
			else:
				helpers.redirect(self, '/', 0)
		else:
			helpers.redirect(self, '/', 0)
		
	def post(self):
		user = users.get_current_user()
		if user:
			# Retrieve data from form
			title = self.request.get('title')
			content = self.request.get('content')
			days = int(self.request.get('days'))
			hours = int(self.request.get('hours'))
			# Convert 'on' or 'off' from checkbox to True or False 
			important_original = self.request.get('important')
			if important_original == 'on':
				important = True
			else:
				important = False
			# Retrieve person and home objects
			person = login.is_roommate_account_initialized(user)
			person_name = Person.query().filter(Person.user_id == person.user_id).fetch()[0].name
			home = Home.query().filter(Home.key == person.home_key).fetch()
			# Calculate expiration time
			cur_time = time.time()
			expir_time = cur_time + days*24*60*60 + hours*60*60
			# Create and put new sticky
			new_sticky = Sticky(title= title, content= content, important= important, author= person_name, home_key= person.home_key, expiration= expir_time)
			new_sticky.put()
			render.render_page(self, 'stickyCreated.html', "Sticky Created")
			helpers.redirect(self, '/dashboard', 1000)



class AssignBillHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				home = Home.query(Home.key == person.home_key).fetch()[0]
				possible_payers = []
				for user_id in home.occupants:
					p = Person.query().filter(Person.user_id == user_id).fetch()[0]
					possible_payers.append(p)
				data = {'payers': possible_payers}
				render.render_page_with_data(self, 'bills.html', 'Assign a Bill', data)
			else:
				helpers.redirect(self, '/', 0)
		else:
			helpers.redirect(self, '/', 0)
	def post(self):
		user = users.get_current_user()
		person = login.is_roommate_account_initialized(user)
		home = Home.query(Home.key == person.home_key).fetch()[0]
		bill_name = self.request.get('bill_name')
		payer_id = self.request.get('payer')
		payer_name = Person.query().filter(Person.user_id == payer_id).fetch()[0].name
		home_key = home.key
		bill = Bills(bill_name=bill_name, home_key = home_key, payer_id=payer_id, payer_name = payer_name)
		bill.put()
		render.render_page(self, 'billsCreated.html', 'Bill Created')
		helpers.redirect(self, '/dashboard', 1000)




class CreateChoreHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				home = Home.query(Home.key == person.home_key).fetch()[0]
				rotation_list = []
				for user_id in home.occupants:
					p = Person.query().filter(Person.user_id == user_id).fetch()[0]
					rotation_list.append(p)
				data = {'rotation_list': rotation_list}
				render.render_page_with_data(self, 'chores.html', 'Create a Chore', data)
			else:
				helpers.redirect(self, '/', 0)
		else:
			helpers.redirect(self, '/', 0)

	def post(self):
		user = users.get_current_user()
		person = login.is_roommate_account_initialized(user)
		home = Home.query(Home.key == person.home_key).fetch()[0]
		home_key = home.key
		chore_name = self.request.get('chore_name')
		duration = int(self.request.get('days'))
		cur_time = time.time()
		duration = duration*24*60*60
		end_time = cur_time + duration
		workers = []
		workers_names = []
		for p in home.occupants:
			if self.request.get(p) == 'on':
				workers.append(p)
				per = Person.query().filter(Person.user_id == p).fetch()[0].name
				workers_names.append(per)
		chore = Chore(home_key= home_key, workers_names = workers_names, chore_name= chore_name, duration=duration, end_time=end_time, workers=workers)
		chore.put()
		render.render_page(self, 'choreCreated.html', 'Chore Created')
		helpers.redirect(self, '/dashboard', 1000)


class DoNotDisturbHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				if(person.do_not_disturb):
					person.do_not_disturb = False
					data = {'dnd_state' : 'Do not disturb is off.'}
					person.put()
				else:
					person.do_not_disturb = True
					data = {'dnd_state' : 'DO NOT DISTURB!'}
					person.put()
					sender_address = 'Roommates <do.not.disturb.roommates@gmail.com>'
					occupants = Home.query().filter(Home.key == person.home_key).fetch()[0].occupants
					for occupant in occupants:
						receipient = Person.query().filter(Person.user_id == occupant).fetch()[0]
						receipient = receipient.email_address
						if receipient == person.email_address:
							logging.info(occupant)
						else:
							helpers.send_dnd_mail(sender_address, person.name, receipient)
				render.render_page_with_data(self, 'doNotDisturb.html', "Do Not Disturb Toggle", data)
				helpers.redirect(self, '/dashboard', 1000)
			else:
				helpers.redirect(self, '/', 0)
		else:
			helpers.redirect(self, '/', 0)



class CheckInOutHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				if(person.location):
					person.location = False
					person.put()
				else:
					person.location = True
					person.put()
				if(person.location):
					data = {'check_in_state' : 'Checked In!'}
				else:
					data = {'check_in_state' : 'Checked Out!'}
				render.render_page_with_data(self, 'checkInState.html', "Check In or Out", data)
				helpers.redirect(self, '/dashboard', 1000)
			else:
			 helpers.redirect(self, '/',0)   
		else:
			helpers.redirect(self, '/',0)




class DeleteStickyHandler(webapp2.RequestHandler):

	def post(self): 
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			sticky_title = self.request.get('sticky_title')
			sticky_content = self.request.get('sticky_content')
			sticky = Sticky.query().filter(Sticky.content==sticky_content, Sticky.title==sticky_title, Sticky.author == person.user_id).fetch()
			sticky = sticky[0]
			sticky.key.delete()
		render.render_page(self, "stickyDeleted.html", "Sticky Deleted!")
		helpers.redirect(self, '/dashboard', 1000)


class ToggleStickyCompletedHandler(webapp2.RequestHandler):
	def post(self): 
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			sticky_title = self.request.get('sticky_title')
			sticky_content = self.request.get('sticky_content')
			sticky_author = self.request.get('sticky_author')
			sticky = Sticky.query().filter(Sticky.content==sticky_content, Sticky.title==sticky_title).fetch()
			sticky = sticky[0]
			if sticky.completed:
				sticky.completed = False
			else:
				sticky.completed = True
			sticky.put()
		render.render_page(self, "stickyToggle.html", "Sticky Completed Toggled")
		helpers.redirect(self, '/dashboard', 1000)



class CompleteChoreHandler(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			person = login.is_roommate_account_initialized(user)
			chore_home_key = person.home_key
			chore_name = self.request.get('chore_name')
			chore_end_time = float(self.request.get('chore_end_time'))
			chore = Chore.query().filter(Chore.chore_name==chore_name, Chore.home_key==chore_home_key).fetch()
			chore = chore[0]
			if chore.completed:
				chore.completed = False
			else:
				chore.completed = True
			chore.put()
		render.render_page(self, "choreCompleted.html", "Chore Completed")
		helpers.redirect(self, '/dashboard', 1000)



class TemplateHandler(webapp2.RequestHandler):
	def get(self):
		# Get current google account that is signed in
		user = users.get_current_user()

		# Check if there is a user signed in
		if user:

			person = login.is_roommate_account_initialized(user)
			if person:
				None

		# If there is no user, prompt client to login
		else:
			helpers.redirect(self, '/',0)




class DeveloperHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			nickname = user.nickname()
			logout_url = users.create_logout_url('/')
			greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
				nickname, logout_url)
		else:
			login_url = users.create_login_url('/')
			greeting = '<a href="{}">Sign in</a>'.format(login_url)

		self.response.write(
			'<html><body>{}</body></html>'.format(greeting))

class SettingsHandler(webapp2.RequestHandler):
	def get(self):
		render.render_page(self, 'settings.html', 'Settings')

class LeaveRoomHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			try:
				#Add mini-form to ask if stickies should be deleted, replace True with var name
				helpers.removeFromRoom(self, user) #Add confirmation for leaving room
				logging.info("No Exception Thrown")
			except AttributeError:
				logging.info("AttributeError thrown")
			helpers.redirect(self, '/newJoinHome', 1000)
		else:
			helpers.redirect(self, '/', 0)
		

class ShareCalendarHandler(webapp2.RequestHandler):
	@decorator.oauth_required
	def get(self):
		# Get current google account that is signed in
		user = users.get_current_user()
		# Check if there is a user signed in
		if user:
			person = login.is_roommate_account_initialized(user)
			if person:
				# Get the authorized Http object created by the decorator.
				http = decorator.http()
				# Call the service using the authorized Http object.
				now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
				requestResults = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute(http=http)

			else:
				helpers.redirect(self, '/',0)
		# If there is no user, prompt client to login
		else:
			helpers.redirect(self, '/',0)

app = webapp2.WSGIApplication([

	('/', MainHandler),
	('/do_not_disturb', DoNotDisturbHandler),
	('/check_in_out', CheckInOutHandler),
	('/create_sticky', CreateStickyHandler),
	('/dashboard', DashboardHandler),
	('/delete_sticky', DeleteStickyHandler),
	# ('/create_account', CreateAccountHandler),
	('/create_home', CreateHomeHandler),
	('/join_home', JoinHomeHandler),
	('/create_calendar', ShareCalendarHandler),
	('/developer', DeveloperHandler),
	('/settings', SettingsHandler),
	('/leaveRoom', LeaveRoomHandler),
	('/newJoinHome', CreateHomeHandler),
	('/create_a_chore', CreateChoreHandler),
	('/complete_sticky', ToggleStickyCompletedHandler),
	('/complete_chore', CompleteChoreHandler),
	('/leaveRoom', LeaveRoomHandler),
	('/assign_bills',AssignBillHandler),
	('/test', TestHandler),
	(decorator.callback_path, decorator.callback_handler()),

], debug=True)
