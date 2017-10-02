# wrapper to start the server
from ledger import app

if __name__ == '__main__':
    app.run(host='0.0.0.0')
