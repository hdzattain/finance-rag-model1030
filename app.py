from flask import Flask, request, jsonify
from rag_inference import generate_recommendation
from strategy_backtesting import run_backtest

app = Flask(__name__)

@app.route("/recommend", methods=["POST"])
def recommend():
    query = request.json.get("query")
    recommendation = generate_recommendation(query)
    return jsonify({"recommendation": recommendation})

@app.route("/backtest", methods=["GET"])
def backtest():
    result = run_backtest()
    return jsonify({"backtest_result": result})

if __name__ == "__main__":
    app.run(debug=True)