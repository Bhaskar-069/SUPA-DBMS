from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import cohere
from config import Config
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Supabase client with options to disable proxy
supabase: Client = create_client(
    Config.SUPABASE_URL, 
    Config.SUPABASE_KEY,
    options={
        "auth": {
            "autoRefreshToken": True,
            "persistSession": True,
            "detectSessionInUrl": False
        }
    }
)

# Initialize Cohere client
co = cohere.Client(Config.COHERE_API_KEY)

# Initialize Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            user_data = response.data[0]
            return User(user_data['id'], user_data['username'])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

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
        
        try:
            response = supabase.table('users').select('*').eq('username', username).execute()
            if response.data:
                user_data = response.data[0]
                if check_password_hash(user_data['password_hash'], password):
                    user = User(user_data['id'], user_data['username'])
                    login_user(user)
                    return redirect(url_for('dashboard'))
            flash('Invalid username or password')
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Check if username exists
            response = supabase.table('users').select('*').eq('username', username).execute()
            if response.data:
                flash('Username already exists')
                return redirect(url_for('register'))
            
            # Create new user
            user_data = {
                'username': username,
                'password_hash': generate_password_hash(password)
            }
            response = supabase.table('users').insert(user_data).execute()
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {e}")
            flash('An error occurred during registration')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    mode = request.args.get('mode', 'all')
    try:
        if mode != 'all':
            response = supabase.table('advice').select('*').eq('mode', mode).order('likes', desc=True).limit(10).execute()
        else:
            response = supabase.table('advice').select('*').order('likes', desc=True).limit(10).execute()
        advices = response.data
    except Exception as e:
        print(f"Dashboard error: {e}")
        advices = []
    return render_template('dashboard.html', advices=advices, current_mode=mode, modes=ADVICE_MODES.keys())

@app.route('/ask_advice', methods=['GET', 'POST'])
@login_required
def ask_advice():
    if request.method == 'POST':
        question = request.form.get('question')
        mode = request.form.get('mode', 'savage')
        
        # Generate advice using Cohere
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
        
        try:
            # Save to Supabase
            advice_data = {
                'question': question,
                'response': advice_response,
                'mode': mode,
                'user_id': current_user.id,
                'likes': 0,
                'dislikes': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            response = supabase.table('advice').insert(advice_data).execute()
            advice_id = response.data[0]['id']
            return redirect(url_for('view_advice', advice_id=advice_id))
        except Exception as e:
            print(f"Error saving advice: {e}")
            flash('An error occurred while saving your advice')
    return render_template('ask_advice.html', modes=ADVICE_MODES.keys())

@app.route('/view_advice/<int:advice_id>')
@login_required
def view_advice(advice_id):
    try:
        response = supabase.table('advice').select('*').eq('id', advice_id).execute()
        if response.data:
            advice = response.data[0]
            return render_template('view_advice.html', advice=advice)
        flash('Advice not found')
    except Exception as e:
        print(f"Error viewing advice: {e}")
        flash('An error occurred while viewing the advice')
    return redirect(url_for('dashboard'))

@app.route('/vote/<int:advice_id>/<action>')
@login_required
def vote(advice_id, action):
    try:
        # Get the advice
        advice_response = supabase.table('advice').select('*').eq('id', advice_id).execute()
        if not advice_response.data:
            return jsonify({'message': 'Advice not found'})
        
        advice = advice_response.data[0]
        
        # Check for existing vote
        vote_response = supabase.table('user_votes').select('*').eq('user_id', current_user.id).eq('advice_id', advice_id).execute()
        
        if vote_response.data:
            existing_vote = vote_response.data[0]
            if existing_vote['vote_type'] == action:
                return jsonify({'message': 'Already voted'})
            
            # Update existing vote
            if action == 'like':
                advice['dislikes'] -= 1
                advice['likes'] += 1
            else:
                advice['likes'] -= 1
                advice['dislikes'] += 1
            
            supabase.table('user_votes').update({'vote_type': action}).eq('id', existing_vote['id']).execute()
        else:
            # Create new vote
            if action == 'like':
                advice['likes'] += 1
            else:
                advice['dislikes'] += 1
            
            vote_data = {
                'user_id': current_user.id,
                'advice_id': advice_id,
                'vote_type': action,
                'created_at': datetime.utcnow().isoformat()
            }
            supabase.table('user_votes').insert(vote_data).execute()
        
        # Update advice likes/dislikes
        supabase.table('advice').update({
            'likes': advice['likes'],
            'dislikes': advice['dislikes']
        }).eq('id', advice_id).execute()
        
        return jsonify({
            'likes': advice['likes'],
            'dislikes': advice['dislikes']
        })
    except Exception as e:
        print(f"Voting error: {e}")
        return jsonify({'message': 'An error occurred while voting'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    try:
        # Get all advice entries for the current user, ordered by most recent first
        response = supabase.table('advice').select('*').eq('user_id', current_user.id).order('created_at', desc=True).execute()
        user_advices = response.data
    except Exception as e:
        print(f"Profile error: {e}")
        user_advices = []
    return render_template('profile.html', user=current_user, advices=user_advices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 