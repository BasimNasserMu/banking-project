from unittest import TestCase
from bank import Transaction


class TestTransaction(TestCase):
    def test_transaction_attributes(self):
        self.transaction = Transaction("deposit", 100, "checking", None, "000001")
        self.assertEqual(self.transaction.type, "deposit")
        self.assertEqual(self.transaction.amount, 100)
        self.assertIsNone(self.transaction.from_acc)
        self.assertEqual(self.transaction.to_acc, "000001")
