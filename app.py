from flask import Flask 
import db
from config import Config
from transcription import transcription_bp
# Initialize the Flask application
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(transcription_bp,url_prefix="/transcription")




    with app.app_context():
        db.create_all()

    return app


app = create_app()





if __name__ == "__main__":
    app.run(debug=True)