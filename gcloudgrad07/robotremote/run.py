import os
from app import create_app, db
from app.models import User

app = create_app()

# Serve a aplicação a porta 5000
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
