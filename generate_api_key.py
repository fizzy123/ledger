# Generates and provides an api key to access the API with.
from ledger.functions import generate_api_key

if __name__ == '__main__':
    print('Use this API key to access the API!')
    print(generate_api_key())
