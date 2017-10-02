import uuid
import csv
import re

from ledger import r_client, db
from ledger.models import Transaction

# generate api key to use to access routes
def generate_api_key():
    key = uuid.uuid4()
    # set key and expire it in a week
    r_client.setex(key, 60 * 60 * 24 * 7, 1)
    return key

# Imports Ledger data from a filename
def import_data(filename):
    with open(filename, newline='\n') as csvfile:
        Transaction.query.delete()
        reader = list(csv.reader(csvfile, delimiter=','))
        for row in reader:
            # Check if sender and recipiant are same. Don't do anything in that case
            if len(row) != 4:
                # pylint: disable=line-too-long
                raise AssertionError('Each row should have 4 comma seperated values. Row: {}'.format(row))
            if row[2] != row[1]:
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", row[0]):
                    # pylint: disable=line-too-long
                    raise AssertionError('First value in csv should be a date with format YYYY-MM-DD. Row: {}'.format(row))
                transaction = Transaction(date=row[0],
                                          recipiant=row[2],
                                          amount=float(row[3]))
                db.session.add(transaction)
                transaction = Transaction(date=row[0],
                                          recipiant=row[1],
                                          amount=-float(row[3]))
                db.session.add(transaction)
        db.session.commit()
        print(filename + " has been added to the database!")
        return
