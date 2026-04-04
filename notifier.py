import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

@app.route("/alert", methods=["POST"])
def alert():
    data = request.get_json()
    status = data.get("status", "firing").upper()
    alerts = data.get("alerts", [])
    lines = []
    for a in alerts:
        summary = a.get("annotations", {}).get("summary", a["labels"].get("alertname"))
        severity = a["labels"].get("severity", "unknown")
        lines.append(f"**[{status}]** {summary} _(severity: {severity})_")
    content = "\n".join(lines) or "Alert received"
    emoji = "🔴" if status == "FIRING" else "✅"
    requests.post(DISCORD_WEBHOOK, json={"content": f"{emoji} {content}"})
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
