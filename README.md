# Overview #

This application provides a ledger report at any given date. The information for this ledger is provided in the setup.


# Requirements #

Python 3  
PostgreSQL  
Redis  


# Setup #
1. Setup a PostgreSQL database for this service to use. If you're not familiar with this process, simply modify `init.sql` with your desired password and then run it.
2. Copy `ledger/settings.py.example` into `ledger/settings.py` and modify it with the proper PostgreSQL settings
3. Either put your csv ledger file in this directory as `ledger.csv` and run
`./setup.sh`

or specify the location of your ledger file in the command.
`./setup.sh location/of/csvfile.csv`


# To run #

```
. env/bin/activate
python runserver.py
```


# To Test #
`py.test tests.py`


# Security #
Routes require an API key in the `X-APIKEY` header. You can use the API key that was provided by the setup script, or you can run `python generate_api_key.py` to generate a new API key. API keys expire in one week.


# Routes #

## Balances ##
`GET /`
### URL Params ###
`date` - Specify date for balances
### Output ###
```
{
  'Jack': 250.00,
  'James': -20.00,
  'Emily': 50.00
}
```

