"""
Class that manages utilies and pulls the cost
"""

import sys
sys.path.insert(1, '/home/ubuntu/scripts/scripts')
from google_stuff.gmail.GmailInterface import *
import datetime
import re

class UtilitiesManager:

    def __init__(self, util_type: str):
        self.util_type = util_type
        self.bill_date = None
        self.bill_price = None
        self.search_query_dict = {
            'from' : None,
            'subject' : None,
            'after' : None,
        }


    def setSearchQuery(self, from_email: str, subject: str, after: datetime) -> None:
        """
        Sets search query dict to pass to Gmail API
        """
        self.search_query_dict = {
            'from' : from_email,
            'subject' : subject,
            'after' : after,
        }
    

    def findPriceFromHTML(self, html_string: str) -> float:
        """
        Uses regex to find the price and returns it as a float \n
        TODO: at some point figure out a better way to parse through the HTML
        """

        regex_price_search = '(\$)(\d+.\d{2})'
        try:
            price = float(re.search(regex_price_search , html_string).group(2))
        except:
            price = None

        return price


    def setBillPrice(self) -> None:
        """
        Sets bill price for utility object from Gmail API
        """
        print('Looking to set a price for', self.util_type)
        gmail_object = GmailInterface()
        message_ids = gmail_object.getMessagesMatchingQuery(self.search_query_dict)
        if not message_ids:
            # TODO set a trigger / alert 
            print('no message_ids')
            return
        html_string = gmail_object.getMessage(message_ids[0]['id'])
        self.bill_price = self.findPriceFromHTML(html_string)
        print('Price found:', self.bill_price)
        if self.util_type == 'pge':
            self.bill_price += 1.35
            self.bill_price = round(self.bill_price, 2)
            print('Adding $1.35 for PGE. New price is {price}'.format(price=self.bill_price))
        if self.util_type == 'interwebs':
            self.bill_price = round(self.bill_price - 75.00,2) if self.bill_price > 75.00 else 0
            print('Subtracting $75 for Wave. New price is {price}'.format(price=self.bill_price))
    



if __name__ == '__main__':
    test = UtilitiesManager('pge')
    test.setSearchQuery('do-not-reply@wavebroadband.com','Thank you for your payment', datetime.date.today())
    test.setBillPrice()
    print(test.bill_price)
    


    


