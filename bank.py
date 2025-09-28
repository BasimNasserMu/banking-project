import csv
from datetime import datetime, timedelta
import uuid
import cutie
from tabulate import tabulate


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
        self.__password = password
        self.__checking_balance = checking_balance
        self.__savings_balance = savings_balance
        self.transaction_history = transaction_history
        self.overdraft_count = overdraft_count
        self.is_active = is_active
        self.tokens_list = []

    class Access_Token:
        def __init__(self, minutes):
            self.token = uuid.uuid4()
            self.expire = datetime.now() + timedelta(minutes=minutes)

    def login(self, password):
        if password == self.__password:
            token = self.Access_Token(2)  # 2 minute session
            self.tokens_list.append(token)
            return [token.token, token.expire]

    def is_authenticated(self, token):
        for accessToken in self.tokens_list:
            if accessToken.token == token:
                if accessToken.expire > datetime.now():
                    return True
                print("\nToken Expired. Login again.")
                return False
        print("\nInvalid Token.")
        return False

    def check_status(self, token=None):
        if self.is_authenticated(token):
            if self.is_active:
                if self.overdraft_count >= 2 or self.__checking_balance <= -100:
                    self.is_active = False
                    print(
                        "\nAccount deactivated due to excessive overdrafts. pay the fees by depositing money or transferring money to reactivate"
                    )
                    return False
                return True
            if not self.is_active:
                if self.__checking_balance >= 0:
                    self.is_active = True
                    self.overdraft_count = 0
                    print(
                        "\nAccount reactivated. Thank you for settling your overdraft fees."
                    )
                    return True
                print(
                    "\nAccount is inactive due to excessive overdrafts. Please deposit money or transfer money to reactivate."
                )
                return False
            return False
        return False

    def get_balance(self, account_type="checking", token=None):
        if self.is_authenticated(token):
            if account_type == "checking":
                return self.__checking_balance
            elif account_type == "savings":
                return self.__savings_balance
        return False

    def deposit(self, amount, account_type="checking", token=None):
        if self.is_authenticated(token) and amount > 0:
            if account_type == "checking":
                self.__checking_balance += amount
            elif account_type == "savings":
                self.__savings_balance += amount
            else:
                print("Invalid account type. Choose 'checking' or 'savings'.")
                return False
            transaction = Transaction(
                "deposit", amount, account_type, None, self.account_id
            )
            self.transaction_history.append(transaction)
            self.check_status(token)
            return transaction
        return False

    def withdraw(self, amount, account_type="checking", token=None):
        if self.is_authenticated(token) and self.check_status(token) and amount > 0:
            if account_type == "checking":
                balance = self.__checking_balance
            elif account_type == "savings":
                balance = self.__savings_balance

            if amount > balance and account_type == "checking":
                print(
                    f"Amount exceeds available balance. overdraft fee applied. Total amount: {amount + 35}"
                )
                amount += 35
                self.overdraft_count += 1
            elif amount > balance:
                print(f"Amount exceeds available balance. withdraw cannot be done.")
                return

            if account_type == "checking":
                self.__checking_balance -= amount
            else:
                self.__savings_balance -= amount
            transaction = Transaction(
                "withdraw", amount, account_type, self.account_id, None
            )
            self.transaction_history.append(transaction)
            self.check_status(token)
            return transaction
        return False

    def transfer_locally(self, amount, to_account_type, token):
        if self.is_authenticated(token) and amount > 0:
            if to_account_type == "savings" and self.check_status(token):
                from_balance = self.__checking_balance
            elif to_account_type == "checking":
                from_balance = self.__savings_balance

            if amount > from_balance and to_account_type == "savings":
                print(
                    f"Amount exceeds available checking balance. overdraft fee applied. Total amount: {amount + 35}"
                )
                amount += 35
                self.overdraft_count += 1
            elif amount > from_balance and to_account_type == "checking":
                print(f"Amount exceeds available balance. withdraw cannot be done.")
                return

            if to_account_type == "checking":
                self.__savings_balance -= amount
                self.__checking_balance += amount
            else:
                self.__checking_balance -= amount
                self.__savings_balance += amount
            transaction = Transaction(
                "local transfer", amount, to_account_type, self.account_id, None
            )
            self.transaction_history.append(transaction)
            self.check_status(token)
            return transaction
        return False

    def transfer(self, amount, to_customer, token=None):
        if self.is_authenticated(token) and self.check_status(token) and amount > 0:
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
            self.transaction_history.append(transaction)
            to_customer.transaction_history.append(transaction)
            self.check_status(token)
            return transaction
        return False


class Bank:
    def __init__(self, name):
        self.name = name
        self.customers = []
        self.transactions = []
        self.current_customer = None
        self.current_token = ""

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
                            is_active=bool(row[6]),
                            overdraft_count=int(row[7]),
                        )
                    )
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)
            if rows:
                for row in rows:
                    if row[0] != "type":
                        transaction = Transaction(
                            transaction_type=row[0],
                            amount=float(row[1]),
                            from_acc=row[2] if row[2] != "None" else None,
                            to_acc=row[3] if row[3] != "None" else None,
                            timestamp=row[4],
                        )
                        self.transactions.append(transaction)
                        for customer in self.customers:
                            if (
                                customer.account_id == transaction.from_acc
                                or customer.account_id == transaction.to_acc
                            ):
                                customer.transaction_history.append(transaction)

    def save_data(self):
        self.handle_current_customer()
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
                    "is_active",
                    "overdraft_count",
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
                        customer.is_active,
                        customer.overdraft_count,
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

    def handle_current_customer(self, customer=None):
        if self.current_customer:
            replaced = False
            for i, c in enumerate(self.customers):
                if c.account_id == self.current_customer.account_id:
                    self.customers[i] = self.current_customer
                    replaced = True
                    break
            if not replaced:
                self.customers.append(self.current_customer)
            self.current_customer = None

        if customer:
            self.current_customer = customer

    def create_account(self, frst_name, last_name, password, opening_balance=0.0):
        if self.customers:
            last_id = max(int(customer.account_id) for customer in self.customers)
            account_id = str(last_id + 1)
        else:
            account_id = "10000"
        new_customer = Customer(
            account_id, frst_name, last_name, password, opening_balance
        )
        self.customers.append(new_customer)
        print(f"Account created successfully. Your account ID is {account_id}")
        return new_customer

    def login(self, customer, password):
        self.current_token = customer.login(password)
        if self.current_token:
            return True
        return False

    def main(self):
        print(f"Welcome to {self.name} Bank!")
        while True:
            print("\nMain Menu:")
            choices = ["Create new Account", "Login to Account", "Exit"]
            choice = cutie.select(choices)
            match choice:
                case 0:
                    print("\nFill out below info:")
                    frst_name = input("First Name: ")
                    last_name = input("Last Name: ")
                    password = cutie.secure_input("Password: ")
                    opening_balance = cutie.get_number("Opening Balance: ")
                    new_account = self.create_account(
                        frst_name, last_name, password, opening_balance
                    )
                    print(
                        f"\nNew Account created with Account ID: {new_account.account_id}.\n"
                    )
                    continue
                case 1:
                    account_list = []
                    for customer in self.customers:
                        account_list.append(
                            f"ID: {customer.account_id}, {customer.frst_name} {customer.last_name}"
                        )
                    print("\nSelect Account to log into:")
                    selected_account_index = cutie.select(account_list)
                    self.handle_current_customer(self.customers[selected_account_index])
                    while True:
                        pd = cutie.secure_input("Enter Account's Password: ")
                        if not self.login(self.current_customer, pd):
                            if not cutie.select(["Try Again.", "Return to main menu."]):
                                continue
                            self.handle_current_customer()
                        break
                    if not self.current_customer:  # Not logged in
                        continue  # Return to Main menu

                    print(
                        f"\nLogged in successfully to Account Id: {self.current_customer.account_id}\nSession Expires at: {self.current_token[1]}"
                    )
                    while True:
                        choices = [
                            "Check Account Status",
                            "Check Balance",
                            "Transaction History",
                            "Deposit",
                            "Withdraw",
                            "Transfer",
                            "Exit",
                        ]
                        match cutie.select(choices):
                            case 0:
                                if self.current_customer.check_status(
                                    self.current_token[0]
                                ):
                                    print("\nAccount is Active")
                            case 1:
                                print(
                                    f"\nChecking balance: {self.current_customer.get_balance('checking', self.current_token[0])}"
                                )
                                print(
                                    f"Savings balance: {self.current_customer.get_balance('savings', self.current_token[0])}"
                                )
                            case 2:
                                transactions_list = []
                                for (
                                    transaction
                                ) in self.current_customer.transaction_history:
                                    transactions_list.append(
                                        [
                                            transaction.type,
                                            transaction.amount,
                                            transaction.account_type,
                                            transaction.from_acc,
                                            transaction.to_acc,
                                            transaction.timestamp,
                                        ]
                                    )
                                if transactions_list != []:
                                    headers = [
                                        "Type",
                                        "Amount",
                                        "Account Type",
                                        "from",
                                        "to",
                                        "Timestamp",
                                    ]
                                    print(
                                        "\n"
                                        + tabulate(
                                            transactions_list,
                                            headers=headers,
                                            tablefmt="grid",
                                            floatfmt="12.2f",
                                        )
                                    )
                                    del transactions_list
                                else:
                                    print("\nNo Transactions.")

                            case 3:
                                print("\nDeposit into:")
                                acc_type = (
                                    "savings"
                                    if cutie.select(
                                        ["Checking Account", "Savings Account"]
                                    )
                                    else "checking"
                                )
                                amount = cutie.get_number("Enter Amount to Deposit:")
                                transaction = self.current_customer.deposit(
                                    amount, acc_type, self.current_token[0]
                                )
                                if isinstance(transaction, Transaction):
                                    self.transactions.append(transaction)
                                    print(
                                        f"{amount} has been deposited, current account balance: {self.current_customer.get_balance(acc_type, self.current_token[0])}\n"
                                    )
                            case 4:
                                print("\nWithdraw from:")
                                acc_type = (
                                    "savings"
                                    if cutie.select(
                                        ["Checking Account", "Savings Account"]
                                    )
                                    else "checking"
                                )
                                print(
                                    f"Current Balance: {self.current_customer.get_balance(acc_type,self.current_token[0])}"
                                )
                                amount = cutie.get_number("Enter Amount to Withdraw:")
                                transaction = self.current_customer.withdraw(
                                    amount, acc_type, self.current_token[0]
                                )
                                if isinstance(transaction, Transaction):
                                    self.transactions.append(transaction)
                                    print(
                                        f"{amount} has been withdrawn, current account balance: {self.current_customer.get_balance(acc_type, self.current_token[0])}\n"
                                    )

                            case 5:
                                print("\nTransfer:")
                                match cutie.select(
                                    [
                                        "From Savings to Checking",
                                        "From Checking to Savings",
                                        "To another account",
                                    ]
                                ):
                                    case 0:
                                        amount = cutie.get_number(
                                            "Amount to transfer: "
                                        )
                                        transaction = (
                                            self.current_customer.transfer_locally(
                                                amount,
                                                "checking",
                                                self.current_token[0],
                                            )
                                        )
                                        if isinstance(transaction, Transaction):
                                            self.transactions.append(transaction)
                                            print(
                                                f"{amount} has transfered to checking, new balance of checking: {self.current_customer.get_balance('checking',self.current_token[0])}\n"
                                            )
                                    case 1:
                                        amount = cutie.get_number(
                                            "\nAmount to transfer: "
                                        )
                                        transaction = (
                                            self.current_customer.transfer_locally(
                                                amount, "savings", self.current_token[0]
                                            )
                                        )
                                        if isinstance(transaction, Transaction):
                                            self.transactions.append(transaction)
                                            print(
                                                f"{amount} has transfered to savings, new balance of savings: {self.current_customer.get_balance('savings',self.current_token[0])}\n"
                                            )

                                    case 2:
                                        print("\nSelect Account to transfer to:")
                                        filtered_customers = [
                                            acc
                                            for acc in self.customers
                                            if acc != self.current_customer
                                        ]
                                        account_list = []
                                        for customer in filtered_customers:
                                            account_list.append(
                                                f"ID: {customer.account_id}, {customer.frst_name} {customer.last_name}"
                                            )
                                        selected_account_index = cutie.select(
                                            account_list
                                        )
                                        to_account = filtered_customers[
                                            selected_account_index
                                        ]
                                        amount = cutie.get_number(
                                            "Enter amount to transfer:"
                                        )
                                        transaction = self.current_customer.transfer(
                                            amount, to_account, self.current_token[0]
                                        )
                                        if isinstance(transaction, Transaction):
                                            self.transactions.append(transaction)
                                            print(
                                                f"{amount} has transfered to account: {to_account.account_id}, new balance of checking: {self.current_customer.get_balance('checking',self.current_token[0])}\n"
                                            )
                            case 6 | _:
                                self.handle_current_customer()
                                break
                        continue
                case 2:
                    self.save_data()
                    print("Changes saved! Goodbye..")
                    break
