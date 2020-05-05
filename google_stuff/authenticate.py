from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.client import Credentials
from apiclient.discovery import build
import httplib2

CLIENTSECRETS_LOCATION = '/home/ubuntu/scripts/google_stuff/gmail/credentials.json'
REDIRECT_URI ='urn:ietf:wg:oauth:2.0:oob' 
SCOPES = [
     ## Choose the scopes relevant for you. Note that the last two are potentially harful.
     'https://www.googleapis.com/auth/gmail.readonly',
    #  'https://www.googleapis.com/auth/userinfo.email',
    #  'https://www.googleapis.com/auth/userinfo.profile',
    #  'https://mail.google.com/'
     
    #  'https://www.googleapis.com/auth/gmail.modify',
    #  'https://www.googleapis.com/auth/gmail.compose',
     ]

flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
import logging
auth_uri = flow.step1_get_authorize_url(REDIRECT_URI)
print(auth_uri)
code = input('paste code: ')
credentials = flow.step2_exchange(code)


storage = Storage('/home/ubuntu/scripts/google_stuff/credentials.txt')
storage.put(credentials)
credentials2 = storage.get()

json = credentials.to_json()
print(json)
credentials2 = Credentials.new_from_json(json)


http = httplib2.Http()
http = credentials.authorize(http)
service = build('gmail', 'v1', http=http)

results = service.users().labels().list(userId='me').execute()
labels = results.get('labels', [])

if not labels:
     print('No labels found.')
else:
     print('Labels:')
     for label in labels:
          print(label['name'])