import csv
from datetime import datetime


class Transaction:
    def __init__(self, transaction_type, amount, from_acc=None, to_acc=None):
        self.type = transaction_type
        self.amount = amount
        self.from_acc = from_acc
        self.to_acc = to_acc
        self.timestamp = datetime.now()


class Customer:
    def __init__(self, account_id, frst_name, last_name, password, balance=0.0):
        self.account_id = account_id
        self.frst_name = frst_name
        self.last_name = last_name
        self.__password = password  # make password private. reference: https://stackoverflow.com/questions/1641219/does-python-have-private-variables-in-classes
        self.__checking_balance = balance
        self.__savings_balance = 0.0
        self.__transaction_history = []
        self.overdraft_count = 0
        self.is_active = True

    def is_authenticated(self, password):
        if password == self.__password:
            return True
        print("Incorrect password. Operation aborted.")
        return False

    def check_status(self, password=None):
        if self.is_authenticated(password):
            if self.is_active:
                if self.overdraft_count >= 2:
                    self.is_active = False
                    print(
                        "Account deactivated due to excessive overdrafts. pay the fees by depositing money or transferring money to reactivate"
                    )
                    return False
                return True
            if not self.is_active:
                if self.__checking_balance >= 0:
                    self.is_active = True
                    print(
                        "Account reactivated. Thank you for settling your overdraft fees."
                    )
                    return True
                print(
                    "Account is inactive due to excessive overdrafts. Please deposit money or transfer money to reactivate."
                )
                return False
            return False
        return False

    def get_balance(self, password=None):
        if self.is_authenticated(password):
            return self.__checking_balance
        return False

    def get_savings_balance(self, password=None):
        if self.is_authenticated(password):
            return self.__savings_balance
        return False

    def get_transaction_history(self, password=None):
        if self.is_authenticated(password):
            return self.__transaction_history
        return False

    def deposit(self, amount, password=None):
        if self.is_authenticated(password):
            self.__checking_balance += amount
            self.__transaction_history.append(
                Transaction("deposit", amount, None, self.account_id)
            )
            self.check_status()
            return True
        return False

    def withdraw(self, amount, password=None):
        if self.is_authenticated(password):
            if self.check_status():
                if amount > self.__checking_balance:
                    print(
                        f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                    )
                    amount += 35
                    self.overdraft_count += 1
                self.__checking_balance -= amount
                self.__transaction_history.append(
                    Transaction("withdraw", amount, self.account_id, None)
                )
                self.check_status()
                return True
            return False
        return False

    def transfer(self, amount, to_customer, password=None):
        if self.is_authenticated(password):
            if self.check_status():
                if amount > self.__checking_balance:
                    print(
                        f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                    )
                    amount += 35
                    self.overdraft_count += 1
                self.__checking_balance -= amount
                to_customer.__checking_balance += amount
                transaction = Transaction(
                    "transfer", amount, self.account_id, to_customer.account_id
                )
                self.__transaction_history.append(transaction)
                to_customer.transaction_history.append(transaction)
                self.check_status()
                return True
            return False
        return False


class Bank:
    pass
