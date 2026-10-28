import urllib.request
import json
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'wagi2026'

# --- BAZA DANYCH W PAMIĘCI CHMURY ---
klienci_baza = {}
id_licznik = 1

# --- WKLEJ TUTAJ SWÓJ LINK Z KROKU 1 ---
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby-Zmo8AboJRsARocmYkRq61NcMYPlpgaMU-Q1tT9GpqOlwuZtFH53AOJGdFfaweQoS/exec"

def wyslij_raport_email(lista_alertow):
    if not lista_alertow or "https://script.google.com/macros/s/AKfycby-Zmo8AboJRsARocmYkRq61NcMYPlpgaMU-Q1tT9GpqOlwuZtFH53AOJGdFfaweQoS/exec" in GOOGLE_SCRIPT_URL:
        return
        
    alerty_tekst = "\n".join(lista_alertow)
    payload = {"alerty": alerty_tekst}
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # Render wysyła bezpieczny sygnał do skryptu Google, brak blokad portów pocztowych!
        req = urllib.request.Request(GOOGLE_SCRIPT_URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=5) as response:
            print("Sygnał wysłany pomyślnie do kuriera Google.")
    except Exception as e:
        print(f"Błąd przekazywania sygnału do Google: {e}")

@app.route('/')
def index():
    if not session.get('zalogowany'): 
        return redirect(url_for('login'))
    
    data_list = list(klienci_baza.values())
    
    do_p = []
    for r in data_list:
        if int(r['rok']) <= 2024:
            do_p.append(f"• {r['firma']} [Waga: {r['model']}, Czujniki: {r['czujniki']}] — ważność mija: {r['koniec']}")
    
    if do_p and session.get('wyslac_mail', True):
        wyslij_raport_email(do_p)
        session['wyslac_mail'] = False 
        
    return render_template('index.html', data=data_list, alerty=do_p)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('u') == 'admin' and request.form.get('p') == 'Wagi2026':
            session['zalogowany'] = True
            session['wyslac_mail'] = True 
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('zalogowany', None)
    session.pop('wyslac_mail', None)
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
    session['wyslac_mail'] = True
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
    session['wyslac_mail'] = True
    return redirect(url_for('index'))

@app.route('/del/<int:uid>')
def delete(uid):
    if uid in klienci_baza:
        del klienci_baza[uid]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
