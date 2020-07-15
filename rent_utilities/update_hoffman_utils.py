"""
Run this script to update Hoffman utils to Splitwise
"""

import sys
sys.path.insert(1, '/home/ubuntu/scripts/scripts')
from rent_utilities.UtilitiesManager import *
from splitwise_stuff.SplitwiseInterface import *
import datetime


wave = {
    'util_type' : 'interwebs',
    'util_name' : 'wave',
    'email' : 'do-not-reply@wavebroadband.com',
    'subject' : 'Thank you for your payment',
}

pge = {
    'util_type' : 'pge',
    'util_name' : 'pge',
    'email' : 'CustomerServiceOnline@billpay.pge.com',
    'subject' : 'Your PG&E Energy Statement is Ready to View',
}

sfpuc = {
    'util_type' : 'water',
    'util_name' : 'sfpuc',
    'email' : 'customerservice@sfwater.org',
    'subject' : 'Your New SFPUC Water Bill!',
}

recology = {
    'util_type' : 'garbage',
    'util_name' : 'recology',
    'email' : 'noreply@recology.com',
    'subject' : 'New Bill Available',
}

utilities_dict = {
    'interwebs' : wave,
    'electricity' : pge,
    'water' : sfpuc,
    'garbage' : recology,
 }

hoffman_splitwise_group_id = 10343208 
# hoffman_splitwise_group_id = 19086415 # Test ID 
payer = 'Aaron'


for util in utilities_dict:
    utils_object = UtilitiesManager(utilities_dict[util]['util_type'])
    utils_object.setSearchQuery(
        from_email=utilities_dict[util]['email'],
        subject=utilities_dict[util]['subject'],
        after=datetime.date.today() - datetime.timedelta(days=30),
    )
    utils_object.setBillPrice()
    print('Submitting', utils_object.util_type, 'for', utils_object.bill_price, 'to Splitwise')
    if not utils_object.bill_price or utils_object.bill_price == 0:
        print('Nevermind...There\'s no bill price. Skipping...')
        print('\n')
        continue
    splitwise = SplitwiseInterface()
    splitwise.addExpense(
        cost = utils_object.bill_price,
        description = utils_object.util_type,
        group_id = hoffman_splitwise_group_id,
        payer = payer
    )
    print('\n')
    