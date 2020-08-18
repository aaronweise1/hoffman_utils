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
from email.mime.text import MIMEText
from apiclient import errors


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


     def createMessage(self, sender: str, to: str, subject: str, message_text: str):
          """
          Create a message for an email.

          Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

          Returns:
          An object containing a base64url encoded email object.
          """
          message = MIMEText(message_text)
          message['to'] = to
          message['from'] = sender
          message['subject'] = subject
          raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes())}
          raw_message['raw']=raw_message['raw'].decode('utf-8')
          return raw_message
     

     def sendMessage(self, message: dict):
          """Send an email message.

          Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

          Returns:
          Sent Message.
          """
          try:
               message = (self.service.users().messages().send(userId='me', body=message).execute())
               print('Message Id: %s' % message['id'])
               return message
          except errors.HttpError as error:
               print('An error occurred: %s' % error)

          




     
if __name__ == '__main__':
     gmail = GmailInterface()

     # read test
     # search_query_dict = {
     #                'from' : 'customerservice@sfwater.org',
     #                'subject' : 'Your New SFPUC Water Bill!',
     #                'after' : '2020/04/01'
     #           }

     # messages = gmail.getMessagesMatchingQuery(search_query_dict)
     # print(messages)
     # print(gmail.getMessage(messages[0]['id']))

     # send test
     # to_send = gmail.createMessage('@gmail.com', '@gmail.com', 'test', 'testing')
     # gmail.sendMessage(to_send)



