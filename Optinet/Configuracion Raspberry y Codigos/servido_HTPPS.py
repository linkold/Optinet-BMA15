from flask import Flask, send_file
import ssl

app = Flask(__name__)

@app.route("/descargar")
def descargar():
    return send_file("datos_Banda.pkl", as_attachment=True)

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("cert.pem", "key.pem")  # Certificado y clave
    app.run(host="0.0.0.0", port=4443, ssl_context=("cert.pem", "key.pem"))

