from unittest import TestCase, expectedFailure
from bank import Customer, Transaction


class TestCustomer(TestCase):
    def setUp(self):
        self.customer = Customer("000001", "Basim", "Nasser", "password123", 100.0)
        self.to_customer = Customer("000002", "Mohammed", "Fawaz", "password456", 50.0)

    def test_accessing_private_password(self):
        with self.assertRaises(AttributeError):
            _ = self.customer.__password

    def test_deposit_with_correct_password(self):
        self.customer.deposit(50, password="password123")
        self.assertEqual(self.customer.get_balance(password="password123"), 150.0)

    def test_deposit_with_incorrect_password(self):
        result = self.customer.deposit(50, password="wrongpassword")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)

    def test_deposit_negative_amount(self):
        result = self.customer.deposit(-10, password="password123")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)

    def test_withdraw_with_correct_password(self):
        self.customer.withdraw(50, password="password123")
        self.assertEqual(self.customer.get_balance(password="password123"), 50.0)

    def test_withdraw_with_incorrect_password(self):
        result = self.customer.withdraw(50, password="wrongpassword")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)

    def test_withdraw_negative_amount(self):
        result = self.customer.withdraw(-10, password="password123")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)

    def test_transfer_with_correct_password_and_sufficient_balance(self):
        result = self.customer.transfer(40.0, self.to_customer, password="password123")
        self.assertIsInstance(result, Transaction)
        self.assertEqual(self.customer.get_balance(password="password123"), 60.0)
        self.assertEqual(self.to_customer.get_balance(password="password456"), 90.0)

    def test_transfer_with_incorrect_password(self):
        result = self.customer.transfer(
            40.0, self.to_customer, password="wrongpassword"
        )
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)
        self.assertEqual(self.to_customer.get_balance(password="password456"), 50.0)

    def test_transfer_negative_amount(self):
        result = self.customer.transfer(-20.0, self.to_customer, password="password123")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance(password="password123"), 100.0)
        self.assertEqual(self.to_customer.get_balance(password="password456"), 50.0)
