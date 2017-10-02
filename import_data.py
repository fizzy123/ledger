# Generates and provides an api key to access the API with.
import sys
from ledger.functions import import_data

if __name__ == '__main__':
    import_data(sys.argv[1])
