import os, sys, threading, webbrowser, logging, traceback
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

def run_cms():
    logging.basicConfig(level=logging.INFO)

    # Dossiers securises Windows
    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
    OMNI_DIR = os.path.join(APPDATA, 'OmniScreenData')
    UPLOAD_FOLDER = os.path.join(OMNI_DIR, 'uploads')
    os.makedirs(OMNI_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    db_path = os.path.join(OMNI_DIR, 'omniscreen.db')

    # CORRECTION EXACTE DES TEMPLATES EN PRODUCTION (EXE)
    if getattr(sys, 'frozen', False):
        # Si on est dans le .exe compile, les dossiers sont dezippes dans le dossier temporaire _MEIPASS
        template_dir = os.path.join(sys._MEIPASS, 'cms', 'templates')
        if not os.path.exists(template_dir):
            template_dir = os.path.join(sys._MEIPASS, 'templates')
    else:
        # En mode developpement
        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'omniscreen-super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    # SYSTEME ANTI-CRASH
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        error_details = traceback.format_exc()
        logging.error(f"Erreur Interne: {error_details}")
        return f"<div style='font-family:sans-serif; padding:40px; background:#0f172a; color:white; height:100vh;'><h1>⚙️ Systeme de Securite OmniScreen</h1><p>Une erreur mineure a ete interceptee. L'application a ete protegee.</p><pre style='background:#1e293b; color:#10b981; padding:20px; border-radius:8px;'>{error_details}</pre><a href='/dashboard' style='color:#3b82f6;'>Retourner a l'accueil</a></div>", 500

    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(150), unique=True)
        password = db.Column(db.String(150))

    class Display(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(150))
        code = db.Column(db.String(50))
        status = db.Column(db.String(50), default="EN LIGNE")

    class MediaItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(150))
        m_type = db.Column(db.String(50)) # 'image', 'video', 'widget_html', 'widget_clock'
        content = db.Column(db.Text)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

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
        return render_template('dashboard.html', user=current_user, active_page='dashboard')

    @app.route('/displays')
    @login_required
    def displays():
        screens = Display.query.all()
        return render_template('displays.html', user=current_user, active_page='displays', displays=screens)

    @app.route('/add_display', methods=['POST'])
    @login_required
    def add_display():
        d = Display(name=request.form.get('name'), code=request.form.get('code'))
        db.session.add(d)
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
            m_type = 'video' if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')) else 'image'
            db.session.add(MediaItem(title=title, m_type=m_type, content=filename))
            db.session.commit()
        return redirect(url_for('media'))

    @app.route('/add_widget', methods=['POST'])
    @login_required
    def add_widget():
        db.session.add(MediaItem(
            title=request.form.get('title'),
            m_type=request.form.get('type'),
            content=request.form.get('html_code')
        ))
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

    @app.route('/uploads/<name>')
    def download_file(name):
        return send_from_directory(app.config["UPLOAD_FOLDER"], name)

    @app.route('/schedule')
    @login_required
    def schedule():
        return render_template('schedule.html', user=current_user, active_page='schedule')

    @app.route('/settings')
    @login_required
    def settings():
        return render_template('settings.html', user=current_user, active_page='settings')

    @app.route('/api/playlist')
    def api_playlist():
        items = MediaItem.query.all()
        playlist = []
        for i in items:
            if i.m_type in ['image', 'video']:
                playlist.append({"type": i.m_type, "url": request.host_url + 'uploads/' + i.content, "duration": 15})
        if not playlist:
            playlist.append({"type": "web", "url": "https://fr.wikipedia.org", "duration": 20})
        return jsonify({"campaigns": [{"items": playlist}]})

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    with app.app_context():
        try:
            db.create_all()
            User.query.first()
            Display.query.first()
            MediaItem.query.first()
        except Exception:
            logging.warning("Migration BDD requise. Reinitialisation securisee...")
            db.drop_all()
            db.create_all()

    def open_browser(): webbrowser.open_new('http://127.0.0.1:5000/')
    threading.Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_cms()
