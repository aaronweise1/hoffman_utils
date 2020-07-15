"""
Access Splitwise via API
"""

from flask import Flask, render_template, redirect, session, url_for, request
from flask import Flask, session, request
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser
from typing import List
from typing import Dict
import sys
sys.path.insert(1, '/home/ubuntu/scripts')
from splitwise_stuff.splitwise_info import *
from random import shuffle


key = getConsumerKey()
secret = getConsumerSecret()


class SplitwiseInterface:

    def __init__(self):
        self.consumer_key = getConsumerKey()
        self.consumer_secret = getConsumerSecret()
        self.oauth_verifier = None
        self.oauth_token = None
        self.access_token = getAccessToken()
        self.login_secret = None
        self.url = None
        self.sObj = Splitwise(self.consumer_key, self.consumer_secret)
        self.sObj.setAccessToken(self.access_token)
    

    def accessCheck(self) -> None:
        """
        Checks for access token. Starts login process if not
        """

        if self.access_token:
            return
        self.access_token = self.login()


    def login(self) -> None:
        """
        Logs into Splitwise. Requires manually entering the token and verifier
        """

        sObj = Splitwise(self.consumer_key, self.consumer_secret)
        self.url, self.login_secret = sObj.getAuthorizeURL()
        print(self.url)
        self.oauth_token = input('token: ')
        self.oauth_verifier = input('verifier: ')
        
    
    def authorize(self) -> None:
        """
        Authorizes app to Splitwise
        """

        if not self.login_secret:
            #TODO trigger error
            self.login()
        

        sObj = Splitwise(self.consumer_key, self.consumer_secret)
        self.access_token = sObj.getAccessToken(
            self.oauth_token,
            self.login_secret,
            self.oauth_verifier
        )
        


    def friends(self) -> List['Friend']:
        """
        Returns list of Friend objects for the current user
        """

        return self.sObj.getFriends()
         

    def getCurrentUser(self) -> 'CurrentUser':
        """
        Returns CurrentUser object for the current user
        """
        return self.sObj.getCurrentUser()


    def getGroup(self, group_id: int) -> 'Group':
        """
        Returns Group object for the given group_id
        """
        return self.sObj.getGroup(group_id)


    def getGroupMemberIDs(self, group: 'Group') -> Dict[str,int]:
        """
        Returns a dict of group members {name:id} from a given Group object
        """
        member_object_list = group.getMembers()
        member_dict = {}
        for member in member_object_list:
            member_dict[member.getFirstName()] = member.getId()
        return member_dict


    def addExpense(self, cost: float, description: str, group_id: int, payer: str) -> None:
        """
        Adds expense to Splitwise group. If expenses don't evenly get 
        distributed, it will randomly assign pennies to even things off
        """
        expense = Expense()
        expense.setCost(str(cost))
        expense.setDescription(description)
        expense.setGroupId(group_id)

        group = self.sObj.getGroup(group_id)
        member_dict = self.getGroupMemberIDs(group)
        member_count = len(member_dict)
        per_person_cost = round(cost/member_count, 2)
        expense_members = []
        print(per_person_cost*member_count, cost)
        for member in member_dict:
            expense_user = ExpenseUser()
            expense_user.setId(member_dict[member])
            expense_user.setFirstName(member)
            expense_user.setOwedShare(str(per_person_cost))
            
            if member == payer:
                expense_user.setPaidShare(cost)
            else:
                expense_user.setPaidShare('0.00')

            expense_members.append(expense_user)
        
        if cost < per_person_cost*member_count:
            remainder = (per_person_cost*float(member_count)) - cost
            shuffle(expense_members)
            i = 0
            while remainder > 0.00:
                owed = float(expense_members[i].getOwedShare())
                owed -= 0.01
                expense_members[i].setOwedShare(str(owed))
                remainder -= 0.01
                if i == member_count-1:
                    i = 0
                else:
                    i += 1

        elif cost > per_person_cost*member_count:
            remainder = round(cost - (per_person_cost*float(member_count)),2)
            print(remainder)
            shuffle(expense_members)
            i = 0
            while remainder > 0.00:
                owed = float(expense_members[i].getOwedShare())
                owed += 0.01
                expense_members[i].setOwedShare(str(owed))
                remainder -= 0.01
                if i == member_count-1:
                    i = 0
                else:
                    i += 1
        
        expense.setUsers(expense_members)
        expenses = self.sObj.createExpense(expense)
        print('Successfully added to Splitwise. Expense ID:', expenses.getId())
                



if __name__ == '__main__':
    test = SplitwiseInterface()
    group_id = 19086415
    my_id = test.getCurrentUser().getId()
    my_name = test.getCurrentUser().getFirstName()

    test.addExpense(99.99, 'testing class', group_id, 'Aaron')
