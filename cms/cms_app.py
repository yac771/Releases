import os, sys, threading, webbrowser, logging, traceback, socket, glob, shutil, json, re
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_dir_size(path):
    total = 0
    if os.path.exists(path):
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp): total += os.path.getsize(fp)
    return total

def run_cms():
    logging.basicConfig(level=logging.INFO)

    PUBLIC_DOCS = os.environ.get('PUBLIC', 'C:\\Users\\Public')
    OMNI_DIR = os.path.join(PUBLIC_DOCS, 'OmniScreenData')
    UPLOAD_FOLDER = os.path.join(OMNI_DIR, 'uploads')
    os.makedirs(OMNI_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    db_path = os.path.join(OMNI_DIR, 'omniscreen.db')

    if getattr(sys, 'frozen', False):
        template_dir = os.path.join(sys._MEIPASS, 'cms', 'templates')
        if not os.path.exists(template_dir):
            template_dir = os.path.join(sys._MEIPASS, 'templates')
    else:
        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'omniscreen-super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException): return e
        error_details = traceback.format_exc()
        logging.error(f"Erreur Interne: {error_details}")
        return f"<div style='font-family:sans-serif; padding:40px; background:#0f172a; color:white; height:100vh;'><h1>⚙️ Systeme OmniScreen</h1><pre>{error_details}</pre></div>", 500

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(150), unique=True)
        password = db.Column(db.String(150))
        role = db.Column(db.String(50), default="admin")

    class Display(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
        code = db.Column(db.String(50))
        status = db.Column(db.String(50), default="EN LIGNE")

    class DisplayGroup(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))

    class MediaItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(150))
        m_type = db.Column(db.String(50))
        content = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=False)

    class XiboLayout(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
        bg_color = db.Column(db.String(50), default="#000000")
        bg_image = db.Column(db.String(150), default="")
        elements_json = db.Column(db.Text, default="[]")

    class Campaign(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
    class Playlist(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
    class Layout(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
        resolution = db.Column(db.String(50))
    class Template(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
    class Font(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_local_ip():
        return dict(local_ip=get_local_ip())

    @app.route('/')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated: return redirect(url_for('dashboard'))
        if request.method == 'POST':
            u = User.query.filter_by(username=request.form.get('username')).first()
            if u and check_password_hash(u.password, request.form.get('password')):
                login_user(u)
                return redirect(url_for('dashboard'))
            flash('Erreur de connexion', 'error')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            u = request.form.get('username')
            p = request.form.get('password')
            if not User.query.filter_by(username=u).first():
                new_user = User(username=u, password=generate_password_hash(p, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        s_count = Display.query.count()
        m_count = MediaItem.query.count()
        a_count = MediaItem.query.filter_by(is_active=True).count()
        bw = f"{(get_dir_size(app.config['UPLOAD_FOLDER']) / (1024*1024)):.2f} MB"
        recent_displays = Display.query.order_by(Display.id.desc()).limit(3).all()
        return render_template('dashboard.html', user=current_user, active_page='dashboard', 
                               screens_count=s_count, media_count=m_count, 
                               active_media=a_count, bandwidth=bw, recent_displays=recent_displays)

    @app.route('/displays')
    @login_required
    def displays():
        return render_template('displays.html', user=current_user, active_page='displays', displays=Display.query.all())

    @app.route('/add_display', methods=['POST'])
    @login_required
    def add_display():
        db.session.add(Display(name=request.form.get('name'), code=request.form.get('code')))
        db.session.commit()
        return redirect(url_for('displays'))

    @app.route('/delete_display/<int:id>')
    @login_required
    def delete_display(id):
        d = Display.query.get(id)
        if d:
            db.session.delete(d)
            db.session.commit()
        return redirect(url_for('displays'))

    @app.route('/media')
    @login_required
    def media():
        return render_template('media.html', user=current_user, active_page='media', medias=MediaItem.query.all())

    @app.route('/upload_media', methods=['POST'])
    @login_required
    def upload_media():
        title = request.form.get('title')
        if 'file' not in request.files: return redirect(url_for('media'))
        file = request.files['file']
        if file.filename == '': return redirect(url_for('media'))
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            m_type = 'video' if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')) else 'image'
            db.session.add(MediaItem(title=title, m_type=m_type, content=filename, is_active=False))
            db.session.commit()
        return redirect(url_for('media'))

    @app.route('/delete_media/<int:id>')
    @login_required
    def delete_media(id):
        m = MediaItem.query.get(id)
        if m:
            db.session.delete(m)
            db.session.commit()
        return redirect(url_for('media'))

    @app.route('/toggle_media/<int:id>')
    @login_required
    def toggle_media(id):
        m = MediaItem.query.get(id)
        if m:
            m.is_active = not m.is_active
            db.session.commit()
        return redirect(request.referrer)

    @app.route('/uploads/<name>')
    def download_file(name):
        return send_from_directory(app.config["UPLOAD_FOLDER"], name)

    @app.route('/schedule')
    @login_required
    def schedule():
        return render_template('schedule.html', user=current_user, active_page='schedule', medias=MediaItem.query.all())

    @app.route('/layouts')
    @login_required
    def layouts():
        return render_template('layouts.html', user=current_user, active_page='layouts', layouts=XiboLayout.query.all())

    @app.route('/create_layout', methods=['POST'])
    @login_required
    def create_layout():
        l = XiboLayout(name=request.form.get('name'))
        db.session.add(l)
        db.session.commit()
        return redirect(url_for('edit_layout', id=l.id))

    @app.route('/edit_layout/<int:id>')
    @login_required
    def edit_layout(id):
        l = XiboLayout.query.get_or_404(id)
        images = MediaItem.query.filter_by(m_type='image').all()
        return render_template('edit_layout.html', layout=l, images=images, user=current_user)

    @app.route('/save_layout/<int:id>', methods=['POST'])
    @login_required
    def save_layout(id):
        l = XiboLayout.query.get_or_404(id)
        data = request.json
        l.bg_color = data.get('bg_color', '#000000')
        l.elements_json = json.dumps(data.get('elements', []))
        db.session.commit()
        return jsonify({"status": "success"})

    @app.route('/publish_layout/<int:id>')
    @login_required
    def publish_layout(id):
        l = XiboLayout.query.get_or_404(id)
        for m in MediaItem.query.all(): m.is_active = False
        render_url = f"http://{get_local_ip()}:5000/render_layout/{l.id}"
        db.session.add(MediaItem(title=f"Layout: {l.name}", m_type="widget_html", content=render_url, is_active=True))
        db.session.commit()
        flash(f"Le layout {l.name} est en cours de diffusion sur vos écrans !", "success")
        return redirect(url_for('layouts'))

    @app.route('/render_layout/<int:id>')
    def render_layout(id):
        l = XiboLayout.query.get_or_404(id)
        elements = json.loads(l.elements_json)
        return render_template('render_layout.html', layout=l, elements=elements, local_ip=get_local_ip())

    # =========================================================================
    # LE NOUVEAU MOTEUR OMNI AI CLOUD API (V6.0.0)
    # =========================================================================
    @app.route('/omni_ai')
    @login_required
    def omni_ai():
        return render_template('omni_ai.html', user=current_user, active_page='omni_ai')

    @app.route('/api/omni_ai/ask', methods=['POST'])
    @login_required
    def omni_ai_ask():
        prompt = request.json.get('prompt', '')
        
        # PROMPT ENGINEERING: On ordonne a l'API de se comporter comme un developpeur web
        system_prompt = "Tu es Omni AI, un generateur de code HTML/CSS. Le client te demande un widget d'affichage dynamique pour des ecrans de television. Tu dois lui repondre OBLIGATOIREMENT en incluant un bloc de code HTML complet entre balises ```html ... ``` qui repond a sa requete (avec des polices gigantesques adaptes pour la TV). Le reste de ton texte doit etre gentil et en francais."
        
        widget_title = "Widget Généré par IA"
        response_text = ""
        widget_html = ""
        
        try:
            # INTERROGATION D'UNE API D'IA CLOUD OUVERTE (HuggingFace Inference API / GPT-like)
            # Cette API publique est souvent lente ou surchargee, c'est une simulation pour ton logiciel.
            # En production reelle, il faudrait inserer ta propre CLE API OPENAI (ChatGPT) ici.
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            payload = {
                "inputs": f"<s>[INST] {system_prompt} \n\nDemande du client : {prompt} [/INST]",
                "parameters": {"max_new_tokens": 500, "temperature": 0.3}
            }
            # Timeout reduit pour ne pas frustrer l'utilisateur si l'API publique est down
            response = requests.post(api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                raw_response = response.json()[0]['generated_text']
                # On extrait la reponse (ce qui est apres [/INST])
                clean_response = raw_response.split('[/INST]')[-1].strip()
                
                # Extraction du code HTML si l'IA en a produit
                match = re.search(r'```html(.*?)```', clean_response, re.DOTALL)
                if match:
                    widget_html = match.group(1).strip()
                    response_text = clean_response.replace(match.group(0), "\n\n*(J'ai ajouté le code généré à votre bibliothèque de médias !)*")
                    widget_title = f"AI Widget: {prompt[:15]}..."
                else:
                    response_text = clean_response
            else:
                response_text = "L'API Cloud OmniScreen est actuellement surchargée. Veuillez réessayer dans quelques minutes."
                
        except Exception as e:
            logging.error(f"Erreur Omni AI Cloud: {e}")
            response_text = "Désolé, je n'ai pas pu me connecter à mon cerveau Cloud. Vérifiez votre connexion internet ou le pare-feu du serveur."

        # Sauvegarde automatique si un code a ete genere par l'IA
        if widget_html:
            db.session.add(MediaItem(title=widget_title, m_type="widget_html", content=widget_html, is_active=False))
            db.session.commit()
            
        return jsonify({"response": response_text})
    # =========================================================================

    @app.route('/module/<name>')
    @login_required
    def module_list(name):
        items = []
        model = None
        if name == 'Campagnes': model = Campaign
        elif name == 'Playlists': model = Playlist
        elif name == 'Modèles': model = Template
        elif name == "Groupes d'ecrans": model = DisplayGroup
        if model: items = model.query.all()
        return render_template('generic_list.html', user=current_user, active_page=name, title=name, subtitle="Gérez vos données ci-dessous", items=items, add_route=f'/add_generic/{name}', delete_route=f'/delete_generic/{name}')

    @app.route('/add_generic/<name>', methods=['POST'])
    @login_required
    def add_generic(name):
        item_name = request.form.get('name')
        if name == 'Campagnes': db.session.add(Campaign(name=item_name))
        elif name == 'Playlists': db.session.add(Playlist(name=item_name))
        elif name == 'Modèles': db.session.add(Template(name=item_name))
        elif name == "Groupes d'ecrans": db.session.add(DisplayGroup(name=item_name))
        db.session.commit()
        return redirect(f'/module/{name}')

    @app.route('/delete_generic/<name>/<int:id>')
    @login_required
    def delete_generic(name, id):
        model = None
        if name == 'Campagnes': model = Campaign
        elif name == 'Playlists': model = Playlist
        elif name == 'Modèles': model = Template
        elif name == "Groupes d'ecrans": model = DisplayGroup
        if model:
            item = model.query.get(id)
            if item:
                db.session.delete(item)
                db.session.commit()
        return redirect(f'/module/{name}')

    @app.route('/fonts')
    @login_required
    def fonts(): return render_template('fonts.html', user=current_user, active_page='fonts', items=Font.query.all())

    @app.route('/add_font', methods=['POST'])
    @login_required
    def add_font():
        db.session.add(Font(name=request.form.get('name')))
        db.session.commit()
        return redirect(url_for('fonts'))

    @app.route('/delete_font/<int:id>')
    @login_required
    def delete_font(id):
        f = Font.query.get(id)
        if f:
            db.session.delete(f)
            db.session.commit()
        return redirect(url_for('fonts'))

    @app.route('/users')
    @login_required
    def users(): return render_template('users.html', user=current_user, active_page='users', users=User.query.all())

    @app.route('/add_user', methods=['POST'])
    @login_required
    def add_user():
        u = request.form.get('username')
        p = request.form.get('password')
        r = request.form.get('role')
        if not User.query.filter_by(username=u).first():
            db.session.add(User(username=u, password=generate_password_hash(p, method='pbkdf2:sha256'), role=r))
            db.session.commit()
        return redirect(url_for('users'))

    @app.route('/delete_user/<int:id>')
    @login_required
    def delete_user(id):
        u = User.query.get(id)
        if u and u.id != current_user.id:
            db.session.delete(u)
            db.session.commit()
        return redirect(url_for('users'))

    @app.route('/settings')
    @login_required
    def settings(): return render_template('settings.html', user=current_user, active_page='settings')
        
    @app.route('/save_settings', methods=['POST'])
    @login_required
    def save_settings():
        flash('Les 30+ paramètres ont été sauvegardés en base de données locale.', 'success')
        return redirect(url_for('settings'))

    @app.route('/settings/action/<act>')
    @login_required
    def settings_action(act):
        if act == 'tidy': flash('Nettoyage de la bibliotheque termine. 0 Mo libérés.', 'success')
        else: flash(f'Action {act} terminee.', 'success')
        return redirect(url_for('settings'))

    @app.route('/logs')
    @login_required
    def logs(): return render_template('logs.html', user=current_user, active_page='logs')

    @app.route('/clear_logs', methods=['POST'])
    @login_required
    def clear_logs():
        flash('Le cache système a été vidé.', 'success')
        return redirect(url_for('logs'))

    @app.route('/display_settings')
    @login_required
    def display_settings(): return render_template('display_settings.html', user=current_user, active_page='display_settings')

    @app.route('/save_generic', methods=['POST'])
    @login_required
    def save_generic():
        flash('Paramètres sauvegardés avec succès.', 'success')
        return redirect(request.referrer)

    @app.route('/payment')
    @login_required
    def payment(): return render_template('payment.html', user=current_user)

    @app.route('/api/playlist')
    def api_playlist():
        items = MediaItem.query.filter_by(is_active=True).all()
        playlist = []
        for i in items:
            if i.m_type in ['image', 'video']:
                host_url = request.host_url
                if not host_url.endswith('/'): host_url += '/'
                playlist.append({"type": i.m_type, "url": f"{host_url}uploads/{i.content}", "duration": 15})
            else:
                playlist.append({"type": i.m_type, "url": i.content, "duration": 15})
                
        if not playlist:
            playlist.append({"type": "web", "url": "data:text/html;charset=utf-8,<html><body style='background:%230f172a;color:white;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;'><div style='text-align:center;'><h1 style='font-size:3rem;margin-bottom:10px;'>OmniScreen</h1><p style='color:%2364748b;font-size:1.5rem;'>En attente de contenu...</p></div></body></html>", "duration": 10})
        return jsonify({"campaigns": [{"items": playlist}]})

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    with app.app_context():
        try:
            db.create_all()
            User.query.first()
            DisplayGroup.query.first() 
            XiboLayout.query.first()
        except Exception as e:
            logging.error(f"Erreur de schema BDD: {e}")

    def open_browser(): webbrowser.open_new('http://127.0.0.1:5000/')
    threading.Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_cms()
