import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.broadcast import broadcast_bp, set_bot_instance
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from bot_runner import start_bot_thread, get_bot_instance

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(broadcast_bp, url_prefix='/api/broadcast')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Start Discord bot in background
    bot_token = os.environ.get('DISCORD_BOT_TOKEN')
    if bot_token:
        print("Starting Discord bot...")
        start_bot_thread(bot_token)
        # Wait a bit for bot to initialize
        import time
        time.sleep(3)
        bot_instance = get_bot_instance()
        set_bot_instance(bot_instance)
        print("Discord bot started successfully")
    else:
        print("WARNING: DISCORD_BOT_TOKEN environment variable not set. Bot will not start.")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
