import random
import string
from datetime import datetime, timedelta

import pytest
from flask import url_for

from ledger import app as flask_app, r_client
from ledger.models import Transaction
from ledger.functions import import_data, generate_api_key

# Make application context accessible to tests
@pytest.fixture
def app():
    flask_app.debug = True
    return flask_app

# generates test inputs. Much more likely to accidentally find a test case that fails
#
# case_count - how many test csvs are created
# transaction_max - max number of transactions per test case
# new_entity_probability - probability that a fresh entity is added to the test_case
def generate_csv_strings(case_count=10, transaction_max=10, new_entity_probability=0.5):
    test_cases = []
    names = [
        "john",
        "mary"
    ]
    for _ in range(0, case_count):
        test_case = []
        # loop over a random number of transactions
        for _ in range(1, random.randint(2, transaction_max)):
            # generate a random date within the last 30 days
            new_date = datetime.now() - timedelta(seconds=random.randrange(30 * 24 * 60 * 60))
            new_date = new_date.strftime('%Y-%m-%d')

            # potentially generate a new name and add it to the list of names
            if random.random() < new_entity_probability:
                names.append(''.join(random.choice(string.ascii_lowercase) for i in range(5)))

            # randomly assign a name as the sender and a different name as the recipiant
            new_sender = random.choice(names)
            new_recipiant = random.choice([name for name in names if name != new_sender])

            # generate a cash amount less than 100.
            new_amount = round(random.random() * 100, 2)
            test_case.append("{},{},{},{}".format(new_date, new_sender, new_recipiant, new_amount))
        test_cases.append(test_case)
    return test_cases

# generates correct query results for a given test_case
def generate_query_results(test_case):
    # results when db is queried without a date
    results = {}
    # results when db is queried with a date
    date_results = {}
    # save the date between now and 30 days ago as the date that should be used to query the db
    query_date = datetime.now() - timedelta(seconds=30 * 24 * 60 * 60 / 2)
    query_date_str = query_date.strftime('%Y-%m-%d')
    for row in test_case:
        row = row.split(',')

        # calculate changes in results
        if not results.get(row[1]):
            results[row[1]] = 0
        if not results.get(row[2]):
            results[row[2]] = 0
        results[row[1]] = results[row[1]] - float(row[3])
        results[row[2]] = results[row[2]] + float(row[3])

        # calculate changes in date_results
        if datetime.strptime(row[0], '%Y-%m-%d') <= query_date:
            if not date_results.get(row[1]):
                date_results[row[1]] = 0
            if not date_results.get(row[2]):
                date_results[row[2]] = 0
            date_results[row[1]] = date_results[row[1]] -  float(row[3])
            date_results[row[2]] = date_results[row[2]] +  float(row[3])

    # remove any empty values and round away imprecision in the float data type
    keys = [key for key, value in results.items()]
    for key in keys:
        if round(results[key], 2):
            results[key] = round(results[key], 2)
        else:
            del results[key]
    keys = [key for key, value in date_results.items()]
    for key in keys:
        if round(date_results[key], 2):
            date_results[key] = round(date_results[key], 2)
        else:
            del date_results[key]

    return {
        'date': query_date_str,
        'results': results,
        'date_results': date_results
    }

TEST_CSV_LOCATION = '/tmp/ledger.csv'

# test the module function import_data
def test_import_data():
    # test randomly generated csvs
    csv_test_cases = generate_csv_strings()
    for test_case in csv_test_cases:
        with open(TEST_CSV_LOCATION, 'w') as f:
            f.write('\n'.join(test_case))
        import_data(TEST_CSV_LOCATION)
        for line in test_case:
            row = line.split(',')
            result = Transaction.query.filter(Transaction.date == row[0],
                                              Transaction.recipiant == row[2],
                                              Transaction.amount == row[3]).first()
            assert result
            result = Transaction.query.filter(Transaction.date == row[0],
                                              Transaction.recipiant == row[1],
                                              Transaction.amount == '-' + row[3]).first()
            assert result

    # ensure that test case with improper date throws appropriate error
    bad_date_test_case = csv_test_cases[0][:]
    bad_date_test_case[0] = 'a' + bad_date_test_case[0]
    with open(TEST_CSV_LOCATION, 'w') as f:
        f.write('\n'.join(bad_date_test_case))
    with pytest.raises(AssertionError) as e:
        import_data(TEST_CSV_LOCATION)
# pylint: disable=line-too-long
    assert 'First value in csv should be a date with format YYYY-MM-DD. Row: {}'.format(bad_date_test_case[0].split(',')) == str(e.value)

    # ensure that test case with improper formatting throws appropriate error
    bad_csv_test_case = csv_test_cases[0][:]
    bad_csv_test_case[0] = bad_csv_test_case[0].replace(',', '.')
    with open(TEST_CSV_LOCATION, 'w') as f:
        f.write('\n'.join(bad_csv_test_case))
    with pytest.raises(AssertionError) as e:
        import_data(TEST_CSV_LOCATION)
    assert 'Each row should have 4 comma seperated values. Row: {}'.format(bad_csv_test_case[0].split(',')) == str(e.value)

    # ensure that test case with improper amount throws appropriate error
    bad_amount_test_case = csv_test_cases[0][:]
    bad_amount_test_case[0] = bad_amount_test_case[0] + 'a'
    with open(TEST_CSV_LOCATION, 'w') as f:
        f.write('\n'.join(bad_amount_test_case))
    with pytest.raises(ValueError) as e:
        import_data(TEST_CSV_LOCATION)

# test the module function generate_api_key
def test_generate_api_key():
    apikey = generate_api_key()
    assert r_client.get(apikey)
    assert r_client.ttl(apikey) <= 60 * 60 * 24 * 7

# test that apikey authentication is enforced
def test_api_key_enforcement(client):
    apikey = generate_api_key()
    response = client.get(url_for('index.balances_view'))
    assert response.status_code == 403
    response = client.get(url_for('index.balances_view'), headers={'X-APIKEY': apikey})
    assert response.status_code == 200

# test balance_view route in flask
def test_balance_view(client):
    csv_test_cases = generate_csv_strings()
    apikey = generate_api_key()

    for i in range(0, len(csv_test_cases)):
        test_case = csv_test_cases[i]
        query_results = generate_query_results(test_case)
        with open(TEST_CSV_LOCATION, 'w') as f:
            f.write('\n'.join(test_case))
        import_data(TEST_CSV_LOCATION)

        # test route without date
        response = client.get(url_for('index.balances_view'), headers={'X-APIKEY': apikey})
        assert response.json == query_results['results']

        # test route with date
        response = client.get(url_for('index.balances_view',
                                      date=query_results['date']),
                              headers={'X-APIKEY': apikey})
        assert response.json == query_results['date_results']
