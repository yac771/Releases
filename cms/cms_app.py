import os, sys, threading, webbrowser, logging, traceback
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException

def run_cms():
    logging.basicConfig(level=logging.INFO)

    APPDATA = os.environ.get('APPDATA', os.path.expanduser('~'))
    OMNI_DIR = os.path.join(APPDATA, 'OmniScreenData')
    os.makedirs(OMNI_DIR, exist_ok=True)
    db_path = os.path.join(OMNI_DIR, 'omniscreen.db')

    # CORRECTION EXPERT DU BUG 500 : 
    # PyInstaller compresse les fichiers dans sys._MEIPASS/cms/templates
    if getattr(sys, 'frozen', False):
        template_dir = os.path.join(sys._MEIPASS, 'cms', 'templates')
    else:
        template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')

    app = Flask(__name__, template_folder=template_dir)
    app.config['SECRET_KEY'] = 'omniscreen-super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

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
        m_type = db.Column(db.String(50))
        content = db.Column(db.Text)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # GESTIONNAIRE D'ERREUR GLOBAL (Anti-Ecran Blanc)
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException): return e
        error_details = traceback.format_exc()
        logging.error(f"Erreur Interne: {error_details}")
        return f"<div style='font-family:sans-serif; padding:40px;'><h1>Erreur Interne Capturée</h1><p>Le systeme a empeche un crash.</p><pre style='background:#1e293b; color:#10b981; padding:20px; border-radius:8px;'>{error_details}</pre></div>", 500

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

    @app.route('/add_widget', methods=['POST'])
    @login_required
    def add_widget():
        title = request.form.get('title')
        m_type = request.form.get('type')
        content = request.form.get('html_code')
        db.session.add(MediaItem(title=title, m_type=m_type, content=content))
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

    @app.route('/schedule')
    @login_required
    def schedule():
        return render_template('schedule.html', user=current_user, active_page='schedule')

    @app.route('/settings')
    @login_required
    def settings():
        return render_template('settings.html', user=current_user, active_page='settings')

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    with app.app_context():
        try:
            db.create_all()
            # Test de surete : si les tables ont ete modifiees depuis une ancienne version, ca plantera ici
            User.query.first()
            Display.query.first()
            MediaItem.query.first()
        except Exception as e:
            logging.warning(f"Changement d'architecture detecte. Reinitialisation de la BDD : {e}")
            db.drop_all()
            db.create_all()

    def open_browser(): webbrowser.open_new('http://127.0.0.1:5000/')
    threading.Timer(1.5, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_cms()
