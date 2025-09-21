import csv
import re
from tkinter import NO


class Transaction:
    def __init__(self, transaction_type, amount, from_acc=None, to_acc=None):
        self.transaction_type = transaction_type
        self.amount = amount
        self.from_acc = from_acc
        self.to = to_acc


class Customer:
    def __init__(self, account_id, frst_name, last_name, password, balance=0.0):
        self.account_id = account_id
        self.frst_name = frst_name
        self.last_name = last_name
        self.password = password
        self.balance = balance
        self.savings_balance = 0.0
        self.transaction_history = []
        self.overdraft_count = 0
        self.is_active = True

    def check_status(self):
        if self.is_active:
            if self.overdraft_count >= 2:
                self.is_active = False
                print(
                    "Account deactivated due to excessive overdrafts. pay the fees by depositing money or transferring money to reactivate"
                )
                return False
            return True
        if not self.is_active:
            if self.balance >= 0:
                self.is_active = True
                print(
                    "Account reactivated. Thank you for settling your overdraft fees."
                )
                return True
            print(
                "Account is inactive due to excessive overdrafts. Please deposit money or transfer money to reactivate."
            )
            return False

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(
            Transaction("deposit", amount, None, self.account_id)
        )
        self.check_status()

    def withdraw(self, amount):
        if self.check_status():
            if amount > self.balance:
                print(
                    f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                )
                amount += 35
                self.overdraft_count += 1
            self.balance -= amount
            self.transaction_history.append(
                Transaction("withdraw", amount, self.account_id, None)
            )
            self.check_status()

    def transfer(self, amount, to_customer):
        if self.check_status():
            if amount > self.balance:
                print(
                    f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                )
                amount += 35
                self.overdraft_count += 1
            self.balance -= amount
            to_customer.balance += amount
            transaction = Transaction(
                "transfer", amount, self.account_id, to_customer.account_id
            )
            self.transaction_history.append(transaction)
            to_customer.transaction_history.append(transaction)
            self.check_status()


class Bank:
    pass
