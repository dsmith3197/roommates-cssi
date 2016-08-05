# Outside Libraries
import jinja2
from google.appengine.api import users

# Initialize Jinja Environment
env = jinja2.Environment(loader= jinja2.FileSystemLoader('templates'))


# Takes a html template, page title, and data list to render page
# Must pass self in as an argument
def render_page_with_data(self, page_html, page_title, data):
    # Create logout url
    logout_url = users.create_logout_url('/')
    # Render header
    header_data = {'title': page_title, 'url': logout_url}
    header = env.get_template('header.html')
    self.response.write(header.render(header_data))
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render(data))
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())

def render_page_with_data_no_header(self, page_html, page_title, data):
    
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render(data))
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())


# Takes a html template and page title to render page
# Must pass self in as an argument
def render_page(self, page_html, page_title):
    # Create logout url
    logout_url = users.create_logout_url('/')
    # Render header
    header_data = {'title': page_title, 'url': logout_url}
    header = env.get_template('header.html')
    self.response.write(header.render(header_data))
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render())
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())

def render_page_without_links_on_header(self, page_html, page_title):
    # Render header
    logout_url = users.create_logout_url('/')
    # Render header
    header_data = {'title': page_title, 'url': logout_url}
    
    header = env.get_template('navBarNoLinks.html')
    self.response.write(header.render(header_data))
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render())
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())


def render_page_without_header(self, page_html, page_title):
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render())
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())

def render_page_without_header_with_data(self, page_html, page_title, data):
    # Render page contents
    page = env.get_template(page_html)
    self.response.write(page.render(data))
    # Render footer
    footer = env.get_template('footer.html')
    self.response.write(footer.render())