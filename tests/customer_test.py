from unittest import TestCase
from bank import Customer, Transaction


class TestCustomer(TestCase):
    def setUp(self):
        self.customer = Customer("000001", "Basim", "Nasser", "password123", 100.0)
        self.to_customer = Customer("000002", "Mohammed", "Fawaz", "password456", 50.0)

    def test_accessing_private_password(self):
        with self.assertRaises(AttributeError):
            _ = self.customer.__password

    def test_login_with_correct_password(self):
        self.assertIsNotNone(self.customer.login(password="password123"))

    def test_login_with_incorrect_password(self):
        self.assertIsNone(self.customer.login(password="WrongPassword"))

    def test_deposit_with_correct_password(self):
        current_token = self.customer.login(password="password123")
        self.customer.deposit(50, token=current_token)
        self.assertEqual(self.customer.get_balance(token=current_token), 150.0)

    def test_deposit_with_incorrect_password(self):
        current_token = self.customer.login(password="WrongPassword")
        result = self.customer.deposit(50, token=current_token)
        self.assertFalse(result)
        current_token = self.customer.login(password="password123")
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)

    def test_deposit_negative_amount(self):
        current_token = self.customer.login(password="password123")
        result = self.customer.deposit(-10, token=current_token)
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)

    def test_withdraw_with_correct_password(self):
        current_token = self.customer.login(password="password123")
        self.customer.withdraw(50, token=current_token)
        self.assertEqual(self.customer.get_balance(token=current_token), 50.0)

    def test_withdraw_with_incorrect_password(self):
        current_token = self.customer.login(password="WrongPassword")
        result = self.customer.withdraw(50, token=current_token)
        self.assertFalse(result)
        current_token = self.customer.login(password="password123")
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)

    def test_withdraw_negative_amount(self):
        current_token = self.customer.login(password="password123")
        result = self.customer.withdraw(-10, token=current_token)
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)

    def test_transfer_with_correct_password_and_sufficient_balance(self):
        current_token = self.customer.login(password="password123")
        current_token2 = self.to_customer.login(password="password456")
        result = self.customer.transfer(40.0, self.to_customer, token=current_token)
        self.assertIsInstance(result, Transaction)
        self.assertEqual(self.customer.get_balance(token=current_token), 60.0)
        self.assertEqual(self.to_customer.get_balance(token=current_token2), 90.0)

    def test_transfer_with_incorrect_password(self):
        current_token = self.customer.login(password="wrongPassword")
        result = self.customer.transfer(40.0, self.to_customer, token=current_token)
        self.assertFalse(result)
        current_token = self.customer.login(password="password123")
        current_token2 = self.to_customer.login(password="password456")
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)
        self.assertEqual(self.to_customer.get_balance(token=current_token2), 50.0)

    def test_transfer_negative_amount(self):
        current_token = self.customer.login(password="password123")
        current_token2 = self.to_customer.login(password="password456")
        result = self.customer.transfer(-20.0, self.to_customer, token=current_token)
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(token=current_token), 100.0)
        self.assertEqual(self.to_customer.get_balance(token=current_token2), 50.0)
