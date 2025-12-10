from flask import Flask, send_from_directory, render_template
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Serve index.html (from templates or root)
@app.route("/")
def index():
    # se index.html está na raiz do repo
    if os.path.exists("index.html"):
        return send_from_directory(".", "index.html")
    return "Index not found", 404

# Serve arquivos estáticos se quiser
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
