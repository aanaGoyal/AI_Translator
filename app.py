from flask import Flask, render_template, request, session
from googletrans import LANGUAGES
from deep_translator import GoogleTranslator
from transliterate import translit
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Sorted language dictionary
languages = dict(sorted(LANGUAGES.items(), key=lambda x: x[1]))

def is_english_word(word):
    return re.match("^[A-Za-z]+$", word)

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ''
    original_text = ''
    source_lang = 'auto'
    target_lang = 'en'

    # Initialize history in session
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        original_text = request.form.get('text', '')
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', 'en')

        try:
            # Perform translation
            translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(original_text)

            # If translating to Hindi, transliterate leftover English words
            if target_lang == 'hi':
                words = translated_text.split()
                final_words = []
                for word in words:
                    if is_english_word(word):
                        try:
                            word = translit(word, 'hi')
                        except:
                            pass
                    final_words.append(word)
                translated_text = ' '.join(final_words)

            translation = translated_text

            # Add to history
            session['history'].append({
                'original': original_text,
                'translated': translated_text,
                'source': languages.get(source_lang, source_lang).title(),
                'target': languages.get(target_lang, target_lang).title()
            })
            session.modified = True

        except Exception as e:
            translation = f"Error: {str(e)}"

    return render_template('index.html',
                           translation=translation,
                           original_text=original_text,
                           languages=languages,
                           source_lang=source_lang,
                           target_lang=target_lang,
                           history=session.get('history', []))

from flask import redirect, session, url_for

@app.route("/clear-history", methods=["GET"])
def clear_history():
    session.pop("history", None)
    return redirect(url_for("index"))  # Redirect to the route that renders the translator page

                           

if __name__ == '__main__':
    app.run(debug=True)
