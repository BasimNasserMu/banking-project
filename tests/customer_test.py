from unittest import TestCase, expectedFailure
from bank import Customer


class TestCustomer(TestCase):
    def setUp(self):
        self.customer = Customer("000001", "Basim", "Nasser", "password123", 100.0)
        self.to_customer = Customer("000002", "Mohammed", "Fawaz", "password456", 50.0)

    def test_deposit_with_correct_password(self):
        self.customer.deposit(50, password="password123")
        self.assertEqual(self.customer.get_balance(password="password123"), 150.0)

    @expectedFailure
    def test_deposit_with_incorrect_password(self):
        result = self.customer.deposit(50, password="wrongpassword")
        self.assertFalse(result)
        self.assertEqual(self.customer.get_balance("password123"), 50.0)

    def test_accessing_private_password(self):
        with self.assertRaises(AttributeError):
            _ = self.customer.__password
