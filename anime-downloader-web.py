from flask import Flask, make_response
app = Flask(__name__)

@app.route("/")
def hello():
	response = make_response("hehehehehhehe")
	response.headers["Content-Disposition"] = "attachment; filename=test.txt"
	return response

if __name__ == "__main__":
    app.run()