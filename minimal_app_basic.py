from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Medical AI Assistant is running! Visit <a href='/help'>Help</a> for more information."

@app.route('/help')
def help_page():
    return "This is the help page. The Medical AI Assistant is a health management tool designed to help you track medications and monitor your health."

if __name__ == '__main__':
    app.run(debug=True) 