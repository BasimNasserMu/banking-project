import csv
from datetime import date, datetime
import time
from bank import Customer


class Transaction:
    def __init__(
        self,
        transaction_type,
        amount,
        account_type="checking",
        from_acc=None,
        to_acc=None,
        timestamp=str(datetime.now()),
    ):
        self.type = transaction_type
        self.amount = amount
        self.account_type = account_type
        self.from_acc = from_acc
        self.to_acc = to_acc
        self.timestamp = timestamp


class Customer:
    def __init__(
        self,
        account_id,
        frst_name,
        last_name,
        password,
        checking_balance=0.0,
        savings_balance=0.0,
        transaction_history=[],
        overdraft_count=0,
        is_active=True,
    ):
        self.account_id = account_id
        self.frst_name = frst_name
        self.last_name = last_name
        self.__password = password  # make password private. reference: https://stackoverflow.com/questions/1641219/does-python-have-private-variables-in-classes
        self.__checking_balance = checking_balance
        self.__savings_balance = savings_balance
        self.__transaction_history = transaction_history
        self.__overdraft_count = overdraft_count
        self.is_active = is_active

    def is_authenticated(self, password):
        if password == self.__password:
            return True
        print("Incorrect password. Operation aborted.")
        return False

    def check_status(self, password=None):
        if self.is_authenticated(password):
            if self.is_active:
                if self.__overdraft_count >= 2:
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

    def get_balance(self, password=None, account_type="checking"):
        if self.is_authenticated(password):
            if account_type == "checking":
                return self.__checking_balance
            elif account_type == "savings":
                return self.__savings_balance
        return False

    def get_transaction_history(self, password=None):
        if self.is_authenticated(password):
            return self.__transaction_history
        return False

    def deposit(self, amount, password=None, account_type="checking"):
        if self.is_authenticated(password):
            if account_type == "checking":
                self.__checking_balance += amount
            elif account_type == "savings":
                self.__savings_balance += amount
            else:
                print("Invalid account type. Choose 'checking' or 'savings'.")
                return False
            self.__transaction_history.append(
                Transaction("deposit", amount, account_type, None, self.account_id)
            )
            self.check_status()
            return True
        return False

    def withdraw(self, amount, password=None, account_type="checking"):
        if self.is_authenticated(password):
            if self.check_status():
                if account_type == "checking":
                    balance = self.__checking_balance
                elif account_type == "savings":
                    balance = self.__savings_balance

                if amount > balance and account_type == "checking":
                    print(
                        f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                    )
                    amount += 35
                    self.__overdraft_count += 1
                elif amount > balance:
                    print(f"Amount exceeds available balance. withdraw cannot be done.")
                    return

                if account_type == "checking":
                    self.__checking_balance -= amount
                else:
                    self.__savings_balance -= amount

                self.__transaction_history.append(
                    Transaction("withdraw", amount, account_type, self.account_id, None)
                )
                self.check_status()
                return True
            return False
        return False

    def transfer_locally(self, amount, to_account_type, password):
        if to_account_type == "checking":
            if self.withdraw(amount, password, "savings"):
                self.deposit(amount, password, to_account_type)
        else:
            self.withdraw(amount, password, "checking")
            self.deposit(amount, password, "savings")

    def transfer(self, amount, to_customer, password=None):
        if self.is_authenticated(password):
            if self.check_status():
                if amount > self.__checking_balance:
                    print(
                        f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                    )
                    amount += 35
                    self.__overdraft_count += 1
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
    def __init__(self):
        self.customers = []
        self.transactions = []
        self.current_customer = None
        self.password = ""

        with open("data/bank.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != "account_id":
                    self.customers.append(
                        Customer(
                            account_id=row[0],
                            frst_name=row[1],
                            last_name=row[2],
                            password=row[3],
                            checking_balance=float(row[4]),
                            savings_balance=float(row[5]),
                        )
                    )
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] != "type":
                    self.transactions.append(
                        Transaction(
                            transaction_type=row[0],
                            amount=float(row[1]),
                            from_acc=row[2] if row[2] != "None" else None,
                            to_acc=row[3] if row[3] != "None" else None,
                            timestamp=row[4],
                        )
                    )

    def save_data(self):
        with open("data/bank.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "account_id",
                    "frst_name",
                    "last_name",
                    "password",
                    "checking_balance",
                    "savings_balance",
                ]
            )
            for customer in self.customers:
                writer.writerow(
                    [
                        customer.account_id,
                        customer.frst_name,
                        customer.last_name,
                        customer._Customer__password,
                        customer._Customer__checking_balance,
                        customer._Customer__savings_balance,
                    ]
                )
        with open("data/transactions.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["type", "amount", "from_acc", "to_acc", "timestamp"])
            for transaction in self.transactions:
                writer.writerow(
                    [
                        transaction.type,
                        transaction.amount,
                        transaction.from_acc,
                        transaction.to_acc,
                        transaction.timestamp,
                    ]
                )

    def find_customer(self, account_id):
        for customer in self.customers:
            if customer.account_id == account_id:
                return customer
        print("Customer not found.")
        return None

    def create_account(self, frst_name, last_name, password):
        if self.customers:
            last_id = max(int(customer.account_id) for customer in self.customers)
            account_id = str(last_id + 1)
        else:
            account_id = "10000"
        new_customer = Customer(account_id, frst_name, last_name, password)
        self.customers.append(new_customer)
        self.save_data()
        print(f"Account created successfully. Your account ID is {account_id}")
        return new_customer

    def login(self, customer, password):
        if customer.is_authenticated(password):
            self.current_customer = password
            print(f"Logged in succcessful to account ID: {customer.account_id}.")
            return True
        return False


bank = Bank()
