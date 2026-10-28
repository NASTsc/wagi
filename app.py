from flask import Flask, render_template, request, redirect, url_for, session, Response
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'wagi2026'

# --- BAZA DANYCH W PAMIĘCI CHMURY ---
klienci_baza = {}
id_licznik = 1

@app.route('/')
def index():
    if not session.get('zalogowany'): 
        return redirect(url_for('login'))
    
    data_list = list(klienci_baza.values())
    
    # SYSTEM ALERTÓW NA ROK 2026
    do_p = []
    for r in data_list:
        if int(r['rok']) <= 2024:
            do_p.append(f"• {r['firma']} [Waga: {r['model']}, Czujniki: {r['czujniki']}] — ważność mija: {r['koniec']}")
        
    return render_template('index.html', data=data_list, alerty=do_p)

@app.route('/pobierz_raport')
def pobierz_raport():
    """Generuje czysty plik tekstowy z listą alertów bezpośrednio w przeglądarce."""
    if not session.get('zalogowany'): 
        return redirect(url_for('login'))
        
    data_list = list(klienci_baza.values())
    tresc = "RAPORT MONITORINGU METROLOGICZNEGO -- NAST CO\n"
    tresc += f"Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    tresc += "==================================================\n\n"
    
    licznik = 0
    for r in data_list:
        if int(r['rok']) <= 2024:
            tresc += f"Firma: {r['firma']}\nKontakt: {r['kontakt']}\nModel wagi: {r['model']}\nCzujniki: {r['czujniki']}\nRok oceny: {r['rok']}\nTermin waznosci: {r['koniec']}\n"
            tresc += "--------------------------------------------------\n"
            licznik += 1
            
    if licznik == 0:
        tresc += "Brak aktywnych urzadzen wymagajacych legalizacji."
        
    return Response(
        tresc,
        mimetype="text/plain",
        headers={"Content-disposition": "attachment; filename=raport_legalizacji.txt"}
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('u') == 'admin' and request.form.get('p') == 'Wagi2026':
            session['zalogowany'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('zalogowany', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add():
    global id_licznik
    f = request.form.get('f')
    j = request.form.get('j')
    m = request.form.get('m')
    c = request.form.get('c')
    r = request.form.get('r')
    
    if not f or not r:
        return redirect(url_for('index'))
        
    r_int = int(r)
    k = f"{r_int+2}-11-30"
    p = f"{r_int+2}-10-31"
    
    klienci_baza[id_licznik] = {
        'id': id_licznik,
        'firma': f,
        'kontakt': j,
        'model': m,
        'czujniki': c,
        'rok': r_int,
        'koniec': k,
        'przypomnienie': p
    }
    id_licznik += 1
    return redirect(url_for('index'))

@app.route('/edit/<int:uid>', methods=['POST'])
def edit(uid):
    if uid in klienci_baza:
        f = request.form.get('f')
        j = request.form.get('j')
        m = request.form.get('m')
        c = request.form.get('c')
        r = request.form.get('r')
        
        if not f or not r:
            return redirect(url_for('index'))
            
        r_int = int(r)
        k = f"{r_int+2}-11-30"
        p = f"{r_int+2}-10-31"
        
        klienci_baza[uid].update({
            'firma': f,
            'kontakt': j,
            'model': m,
            'czujniki': c,
            'rok': r_int,
            'koniec': k,
            'przypomnienie': p
        })
    return redirect(url_for('index'))

@app.route('/del/<int:uid>')
def delete(uid):
    if uid in klienci_baza:
        del klienci_baza[uid]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
