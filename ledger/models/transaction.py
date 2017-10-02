# Transaction model schema

from ledger import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), nullable=False)
    recipiant = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)

    def __init__(self, date, recipiant, amount):
        self.date = date
        self.recipiant = recipiant
        self.amount = amount

    def dictify(self):
        return {
            'id': self.id,
            'date': self.date,
            'recipiant': self.recipiant,
            'amount': self.amount
        }

    def __repr__(self):
        return '<Transaction %r: %r>' % (self.recipiant, self.amount)
