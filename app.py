from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3
from dotenv import load_dotenv


def create_app():

    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-me')
    app.config['DATABASE'] = os.path.join(app.root_path, 'dermaai.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MODELS_DIR'] = os.path.join(app.root_path, 'models')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Database helpers
    def get_db_connection():
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            """
        )
        conn.commit()
        conn.close()

    # Initialize database once at startup (Flask 3.x removed before_first_request)
    init_db()

    # Auth routes (simple demo, not production secure)
    @app.route('/')
    def index():
        return render_template('index.html')

    ALLOWED_NEXT = {'/','/skin/','/nail/','/chat/','/routine/','/profile','/profile/'}

    def _normalize_next(url: str) -> str:
        if not url:
            return '/'
        # strip domain if accidentally included
        if '://' in url:
            try:
                from urllib.parse import urlparse
                p = urlparse(url)
                url = p.path or '/'
            except Exception:
                return '/'
        # decode percent-encodings
        try:
            from urllib.parse import unquote
            url = unquote(url)
        except Exception:
            pass
        # ensure leading slash
        if not url.startswith('/'):
            url = '/' + url
        # normalize feature paths to include trailing slash
        if url in ['/skin','/nail','/chat','/routine']:
            url += '/'
        return url

    def _is_safe_next(url: str) -> bool:
        url = _normalize_next(url)
        return any(url.rstrip('/') == allowed.rstrip('/') for allowed in ALLOWED_NEXT)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        next_url = request.args.get('next', '')
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            next_target = _normalize_next(request.form.get('next') or request.args.get('next', ''))
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
            conn.close()
            if user:
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                flash('Signed in successfully', 'success')
                if _is_safe_next(next_target):
                    return redirect(next_target)
                return redirect('/')
            flash('Invalid credentials', 'error')
        return render_template('login.html', next_url=next_url)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            email = request.form.get('email')
            password = request.form.get('password')
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)',
                    (first_name, last_name, email, password)
                )
                conn.commit()
                flash('Account created. Redirecting to sign in…', 'success')
                # Show message on signup page, then auto-redirect via JS
                return render_template('signup.html', redirect_to_login=True)
            except sqlite3.IntegrityError:
                flash('Email already registered', 'error')
            finally:
                conn.close()
        return render_template('signup.html', redirect_to_login=False)

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Signed out', 'info')
        return redirect(url_for('index'))

    # Register feature blueprints
    from features.skin import skin_bp
    from features.nail import nail_bp
    from features.chatbot import chatbot_bp
    from features.routine import routine_bp

    app.register_blueprint(skin_bp, url_prefix='/skin')
    app.register_blueprint(nail_bp, url_prefix='/nail')
    app.register_blueprint(chatbot_bp, url_prefix='/chat')
    app.register_blueprint(routine_bp, url_prefix='/routine')

    # Profile routes
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if not session.get('user_id'):
            return redirect('/login?next=/profile')
        user_id = session['user_id']
        conn = get_db_connection()
        if request.method == 'POST':
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            email = request.form.get('email')
            try:
                conn.execute('UPDATE users SET first_name=?, last_name=?, email=? WHERE id=?',
                             (first_name, last_name, email, user_id))
                conn.commit()
                session['user_email'] = email
                flash('Profile updated', 'success')
            except sqlite3.IntegrityError:
                flash('Email already in use', 'error')
        user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
        conn.close()
        return render_template('profile.html', user=user)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


