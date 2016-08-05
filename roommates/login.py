# Models 
from person import Person
from home import Home 
from sticky import Sticky
import render

# Outside Libraries
from google.appengine.api import users
import jinja2
import os

# Initialize Jinja Environment
env = jinja2.Environment(loader= jinja2.FileSystemLoader('templates'))

# Renders login page with a url to login with google
# Must pass in self when using
def render_login_page(self):
    # Create google login url
    login_url = users.create_login_url('/')
    data = {'url': login_url}
    # Render page contents
    page = env.get_template('login.html')
    self.response.write(page.render(data))



# Takes a user object as input and checks if that  google user has a roommate account set up. 
# Returns person object if so, else returns None
def is_roommate_account_initialized(user):
    if user:
        # Check if user has an account set up
        people = Person.query().fetch()
        for individual in people:
            if user.user_id() == individual.user_id:
                # return current person object
                return individual
    return None

def is_in_room(self, person):
    if person.home_key:
        return True
    return False


# Renders page for current client to create a roommate account
# Must pass in self when using  
def initialize_roommate_account(self):
        render.render_page_without_header(self, 'createAccount.html', 'Create Account')