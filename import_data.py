# wrapper for the module function import_data
import sys
from ledger.functions import import_data

if __name__ == '__main__':
    import_data(sys.argv[1])
