"""
Accesses gmail account via gmail API
"""

from typing import List
from typing import Dict
from oauth2client.file import Storage
from apiclient.discovery import build
import httplib2
import base64
import email

ACCESS_TOKEN = '/home/ubuntu/scripts/google_stuff/gmail/access_token.txt'

class GmailInterface:

     storage = Storage(ACCESS_TOKEN)
     credentials = storage.get()
     http = httplib2.Http()
     http = credentials.authorize(http)
     service = build('gmail', 'v1', http=http)


     def __init__(self):
          pass


     def getLabels(self) -> List[str]:
          """returns labels for gmail account"""

          results = self.service.users().labels().list(userId='me').execute()
          labels = results.get('labels', [])

          return labels


     def getMessage(self, msg_id: str) -> str:
          """
          returns the HTML of an email from a given msg_id as a string
          """
          message = self.service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
          msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
          mime_msg = email.message_from_bytes(msg_str)
          message_main_type = mime_msg.get_content_maintype()
          
          if message_main_type == 'multipart':
               for part in mime_msg.get_payload():
                    if part.get_content_maintype() == 'text':
                         return part.get_payload()
          elif message_main_type == 'text':
               return mime_msg.get_payload()


     def getMessagesMatchingQuery(self, search_query_dict: Dict[str, str]) -> List[Dict[str, str]]:
          """
          returns a list of dicts of messageIDs and threadIDs\n
          Example (not all are required): \n
          search_query_dict = {
               'from' : sender,
               'to' : recipient,
               'subject' : subject,
               'label' : label,
               'after' : sent_after, # YYYY/MM/DD
               'before' : sent_before, # YYYY/MM/DD
               'phrase' : phrase,
          }
          """

          valid_operators = [
               'from',
               'to',
               'subject',
               'label',
               'after',
               'before',
               'phrase',
          ]

          search_query = ''
          for operator in search_query_dict:
               if operator in valid_operators:
                    search_query += '{query_type}:{query}'.format(
                         query_type=operator, 
                         query=search_query_dict[operator]
                    )
                    search_query += ' '
          
          results = self.service.users().messages().list(userId='me', q=search_query).execute()
          messages_ids = results.get('messages', [])
          error = 'No messages found.'
          if not messages_ids:
               print(error)
               # return [error]
          
          return messages_ids


          # messages = []
          # for message_id in messages_ids:
          #      messages.append(self.getMessage(message_id['id']))

          # return messages

          




     
if __name__ == '__main__':
     gmail = GmailInterface()


     search_query_dict = {
                    'from' : 'customerservice@sfwater.org',
                    'subject' : 'Your New SFPUC Water Bill!',
                    'after' : '2020/04/01'
               }

     messages = gmail.getMessagesMatchingQuery(search_query_dict)
     print(messages)
     print(gmail.getMessage(messages[0]['id']))



