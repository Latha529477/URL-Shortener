import os
import sqlite3
import string
import random
from flask import Flask, request, redirect, render_template_string, abort

app = Flask(__name__)
DB_FILE = "urls.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short TEXT UNIQUE,
                original TEXT,
                clicks INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def save_url_mapping(short, original):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short, original))
    conn.commit()
    conn.close()

def get_original_url(short):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT original FROM urls WHERE short = ?", (short,))
    result = c.fetchone()
    if result:
        c.execute("UPDATE urls SET clicks = clicks + 1 WHERE short = ?", (short,))
        conn.commit()
        conn.close()
        return result[0]
    conn.close()
    return None

HTML_TEMPLATE = '''
<!doctype html>
<title>URL Shortener</title>
<h2>Enter a URL to shorten</h2>
<form method="post">
  <input type="url" name="original_url" required style="width: 300px;">
  <input type="submit" value="Shorten">
</form>
{% if short_url %}
  <p>Short URL: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a></p>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_id = generate_short_id()
        save_url_mapping(short_id, original_url)
        short_url = request.host_url + short_id
    return render_template_string(HTML_TEMPLATE, short_url=short_url)

@app.route('/<short_id>')
def redirect_short_url(short_id):
    original_url = get_original_url(short_id)
    if original_url:
        return redirect(original_url)
    else:
        abort(404)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

