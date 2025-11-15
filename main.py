from flask import Flask, request, render_template_string
import pandas as pd
import requests
import io

app = Flask(__name__)

URL_CATALOGO = "https://www.dropbox.com/s/zkp7eo8f2tnlsneemqvjx/catalogo.xlsx?dl=1"
URL_DEWEY = "https://www.dropbox.com/s/wynic8v2mt51cfk0es5m4/Argomenti.xlsx?dl=1"

def carica_dati():
    r1 = requests.get(URL_CATALOGO)
    catalogo = pd.read_excel(io.BytesIO(r1.content))
    r2 = requests.get(URL_DEWEY)
    dewey = pd.read_excel(io.BytesIO(r2.content))
    return catalogo, dewey

def cerca_libri(argomento):
    catalogo, dewey = carica_dati()
    try:
        dewey_id = dewey.loc[dewey['Argomento'].str.contains(argomento, case=False), 'IDArgomento'].values[0]
    except IndexError:
        return []
    libri = catalogo[catalogo['IDArgomento'] == dewey_id]
    return libri[['Titolo', 'Autore', 'Collocazione']].to_dict(orient='records')

@app.route("/", methods=['GET', 'POST'])
def home():
    risultato = []
    if request.method == 'POST':
        domanda = request.form.get("domanda")
        risultato = cerca_libri(domanda)
    return render_template_string("""
        <h2>Chat Catalogo Libri</h2>
        <form method="post">
            Inserisci l'argomento: <input type="text" name="domanda">
            <input type="submit" value="Cerca libri">
        </form>
        {% if risultato %}
            <h3>Libri trovati:</h3>
            <ul>
            {% for libro in risultato %}
                <li>{{libro['Titolo']}} - {{libro['Autore']}} - {{libro['Collocazione']}}</li>
            {% endfor %}
            </ul>
        {% endif %}
    """, risultato=risultato)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
