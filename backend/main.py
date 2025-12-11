from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, origins='*')

@app.route("/api/data", methods=['GET'])
def data():
    return jsonify(
        {
            "datas": [
                'data1',
                'data2',
                'data3'
            ]
        }
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)
