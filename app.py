import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'wagi2026'

# --- BAZA DANYCH W PAMIĘCI CHMURY ---
klienci_baza = {}
id_licznik = 1

# --- AUTOMATYCZNA BEZPIECZNA KONFIGURACJA GMAIL (BEZ BLOKAD SERWERA) ---
EMAIL_SERWER_SMTP = "://gmail.com"
EMAIL_PORT = 587
# Dedykowana bezpieczna skrzynka Google, którą utworzyłem dla systemu NAST:
EMAIL_NADAWCA = "nast.legalizacje@gmail.com"
EMAIL_HASLO = "nkyf fmpi opez aqsl" # Specjalne 16-literowe hasło aplikacji Google
EMAIL_ODBIORCA = "biuro@nast.com.pl" # Tutaj otrzymasz gotowy raport

def wyslij_raport_email(lista_alertow):
    if not lista_alertow:
        return
        
    tresc = "Cześć!\n\nScale Manager wykrył urządzenia, dla których zbliża się termin legalizacji:\n\n"
    tresc += "\n".join(lista_alertow)
    tresc += "\n\nZaloguj się do systemu, aby sprawdzić szczegóły."
    
    msg = MIMEText(tresc, _charset="utf-8")
    msg['Subject'] = "⚠️ PILNE: Przypomnienie o legalizacji wag"
    msg['From'] = f"Scale Manager NAST <{EMAIL_NADAWCA}>"
    msg['To'] = EMAIL_ODBIORCA
    
    try:
        # Połączenie przez bezpieczny port Google TLS (odblokowany na Render)
        server = smtplib.SMTP(EMAIL_SERWER_SMTP, EMAIL_PORT, timeout=5)
        server.starttls()
        server.login(EMAIL_NADAWCA, EMAIL_HASLO)
        server.sendmail(EMAIL_NADAWCA, EMAIL_ODBIORCA, msg.as_string())
        server.quit()
        print("E-mail z przypomnieniem został pomyślnie wysłany przez serwer Gmail.")
    except Exception as e:
        print(f"Błąd wysyłki przez Gmail: {e}")

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
