from flask import Flask
from config import Config
from lms_app import create_app


app = create_app(Config)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
    except Exception as e:
        print(f"Error starting the application: {e}")
