from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow


def get_credentials():
	flow = OAuth2WebServerFlow(client_id='270567588357-nnleha1dmgvgr7jatb1du51ruvqn4mou.apps.googleusercontent.com',
                           client_secret='cAn4N7YIjckbjRaHWNqp1OEZ',
                           scope='https://www.googleapis.com/auth/calendar',
                           redirect_uri='http://localhost:9080/receive_credentials')
