from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import cohere
from config import Config
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Cohere client
co = cohere.Client(Config.COHERE_API_KEY)

# Define advice modes with spicier prompts
ADVICE_MODES = {
    'savage': """You are the meanest, most brutally honest roast comedian. Channel your inner Gordon Ramsay and Don Rickles. 
                Absolutely destroy them with your response, but make it clever and hilarious. Use creative insults and brutal honesty.
                Be as savage as possible while being funny. Maximum savagery, minimum sympathy. Keep it under 50 words.
                For this soul who needs a reality check: """,
    
    'funny': """You're a witty comedian doing a standup routine. Think Dave Chappelle meets John Mulaney.
                Make your response absolutely hilarious with clever observations and unexpected punchlines.
                Go wild with the humor, use wordplay, and make them laugh out loud. Keep it under 50 words.
                Here's your comedy prompt: """,
    
    'revenge': """You are a master of psychological warfare and legal revenge. Your goal is to suggest the most diabolically clever ways to get back at someone without breaking any laws.
                 Focus on social manipulation, reputation damage, and karma-inducing schemes that will make them regret their actions.
                 Be specific about revenge tactics like: spreading embarrassing truths, turning their friends against them, or making them jealous of your success.
                 Make your revenge suggestions detailed, creative, and satisfying. Keep it under 100 words.
                 For this person seeking sweet revenge: """,
    
    'moody': """You are a dramatically depressed poet who sees the dark beauty in everything.
                Channel Edgar Allan Poe meets Sylvia Plath at a rainy coffee shop.
                Use dark metaphors, stormy imagery, and deep emotional undertones.
                Make it beautifully melancholic but with a hint of hope. Keep it under 50 words.
                For this troubled soul: """,
    
    'wholesome': """You are the most supportive, encouraging friend who still keeps it real.
                   Think Ted Lasso meets Bob Ross, with a dash of tough love when needed.
                   Be uplifting and positive, but don't sugar-coat the truth.
                   Make them feel motivated while being honest. Keep it under 50 words.
                   For this friend seeking guidance: """
}

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}/{Config.MYSQL_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    advices = db.relationship('Advice', backref='author', lazy=True)

class Advice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(20), nullable=False, default='savage')
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    advice_id = db.Column(db.Integer, db.ForeignKey('advice.id'), nullable=False)
    vote_type = db.Column(db.Enum('like', 'dislike'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    mode = request.args.get('mode', 'all')
    if mode != 'all':
        top_advices = Advice.query.filter_by(mode=mode).order_by(Advice.likes.desc()).limit(10).all()
    else:
        top_advices = Advice.query.order_by(Advice.likes.desc()).limit(10).all()
    return render_template('dashboard.html', advices=top_advices, current_mode=mode, modes=ADVICE_MODES.keys())

@app.route('/ask_advice', methods=['GET', 'POST'])
@login_required
def ask_advice():
    if request.method == 'POST':
        question = request.form.get('question')
        mode = request.form.get('mode', 'savage')
        
        # Generate advice using Cohere with improved prompts
        prompt = ADVICE_MODES[mode] + question
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=100,
            temperature=0.9,
            k=0,
            p=0.75,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )
        
        advice_response = response.generations[0].text.strip()
        
        # Save to database
        advice = Advice(
            question=question,
            response=advice_response,
            mode=mode,
            user_id=current_user.id
        )
        db.session.add(advice)
        db.session.commit()
        
        return redirect(url_for('view_advice', advice_id=advice.id))
    return render_template('ask_advice.html', modes=ADVICE_MODES.keys())

@app.route('/view_advice/<int:advice_id>')
@login_required
def view_advice(advice_id):
    advice = Advice.query.get_or_404(advice_id)
    return render_template('view_advice.html', advice=advice)

@app.route('/vote/<int:advice_id>/<action>')
@login_required
def vote(advice_id, action):
    advice = Advice.query.get_or_404(advice_id)
    existing_vote = UserVote.query.filter_by(
        user_id=current_user.id,
        advice_id=advice_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == action:
            return jsonify({'message': 'Already voted'})
        
        # Change vote
        if action == 'like':
            advice.dislikes -= 1
            advice.likes += 1
            existing_vote.vote_type = 'like'
        else:
            advice.likes -= 1
            advice.dislikes += 1
            existing_vote.vote_type = 'dislike'
    else:
        # New vote
        if action == 'like':
            advice.likes += 1
            vote_type = 'like'
        else:
            advice.dislikes += 1
            vote_type = 'dislike'
        
        new_vote = UserVote(
            user_id=current_user.id,
            advice_id=advice_id,
            vote_type=vote_type
        )
        db.session.add(new_vote)
    
    db.session.commit()
    return jsonify({
        'likes': advice.likes,
        'dislikes': advice.dislikes
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    # Get all advice entries for the current user, ordered by most recent first
    user_advices = Advice.query.filter_by(user_id=current_user.id).order_by(Advice.created_at.desc()).all()
    return render_template('profile.html', user=current_user, advices=user_advices)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True) 