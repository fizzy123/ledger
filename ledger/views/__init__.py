from ledger import app
from .index import index_blueprint
app.register_blueprint(index_blueprint)
