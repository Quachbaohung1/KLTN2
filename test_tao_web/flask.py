from flask import Flask
app = Flask(__name__)

@app.route("/abc")
def main():
    return "welcom!"

if __name__ == "__main__":
    app.run()