from flask import Flask, render_template
from sentiments import second
import os


app = Flask(__name__)

# initializing the user cookie
app.secret_key = os.urandom(24)

# blueprint to call the second python file in the project.
app.register_blueprint(second)


# call the Home template when the url is http://localhost:5000/
@app.route('/')
def home():
	return render_template('home.html')


if __name__ == "__main__":
	app.run(debug=True)
