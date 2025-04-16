import mysql.connector
from config import Config
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

# Sample data
SAMPLE_USERS = [
    "relationship_guru",
    "love_doctor",
    "heart_healer",
    "advice_master",
    "wisdom_keeper"
]

SAMPLE_QUESTIONS = {
    'savage': [
        "My boyfriend keeps leaving dirty dishes in the sink. What should I do?",
        "My girlfriend takes 2 hours to get ready every time we go out. Help?",
        "My partner keeps telling the same boring story at parties. Thoughts?",
        "My roommate never replaces the toilet paper roll. Ideas?",
        "My date spent our entire dinner texting. What next?",
        "My ex wants to 'stay friends' but keeps flirting with me. Advice?",
        "My partner's cooking is terrible but they love cooking for me. What do I do?",
        "My friend keeps setting me up with terrible dates. How do I make it stop?",
        "My coworker keeps stealing my lunch from the office fridge. Solutions?",
        "My sister's boyfriend is clearly using her for money. How do I tell her?"
    ],
    'funny': [
        "I accidentally liked my ex's Instagram post from 3 years ago. What now?",
        "I called my boss 'mom' during a meeting. How do I recover?",
        "I sent a spicy text to my mom instead of my boyfriend. Help!",
        "My date showed up in a matching outfit as me. What's the protocol here?",
        "I forgot my anniversary but my partner forgot too. Should we celebrate twice?",
        "I've been faking being a Star Wars fan for my partner. When do I confess?",
        "My partner caught me dancing to their playlist when home alone. How embarrassing?",
        "I pretended to know wine at a fancy dinner and now I'm hosting a tasting. Help!",
        "I've been using a fake accent to impress someone. How do I break it to them?",
        "My partner found my secret snack stash. How do I explain the quantity?"
    ],
    'revenge': [
        "My friend ghosted me after borrowing money. How do I get even?",
        "My ex spread rumors about me at work. What's a professional response?",
        "Someone keeps stealing my parking spot. Ideas for payback?",
        "My roommate ate my labeled leftovers. How do I return the favor?",
        "My sibling broke my favorite mug and denied it. Revenge suggestions?",
        "My neighbor keeps playing loud music at 3AM. What's a creative solution?",
        "My coworker took credit for my project. How to handle this?",
        "Someone copied my business idea. What's the best way forward?",
        "My friend ditched our plans for a better offer. How to respond?",
        "My partner's ex keeps 'accidentally' running into us. Ideas?"
    ],
    'moody': [
        "Why do relationships have to be so complicated?",
        "Is love worth all this pain and uncertainty?",
        "Why do people change after getting into a relationship?",
        "Does anyone else feel lonely even when surrounded by people?",
        "Why do we keep making the same relationship mistakes?",
        "Is it normal to miss someone who was toxic for you?",
        "Why do good things always seem to end?",
        "How do you know if you're meant to be alone?",
        "Why do people ghost instead of being honest?",
        "Does the pain of heartbreak ever really go away?"
    ],
    'wholesome': [
        "How do I show my partner I appreciate them more?",
        "What are some ways to make someone's day special?",
        "How can I be a better friend to those around me?",
        "What are some meaningful ways to say 'I love you'?",
        "How do I support my friend through their breakup?",
        "What are some ways to build trust in a relationship?",
        "How can I show my family I care about them more?",
        "What are some ways to make new friends as an adult?",
        "How do I maintain long-distance friendships?",
        "What are some ways to practice self-love?"
    ]
}

SAMPLE_RESPONSES = {
    'savage': [
        "Have you tried putting the dishes on their pillow? Nothing says 'I care' like marinara sauce on Egyptian cotton.",
        "Tell them you're charging by the hour for waiting time. Your time is money, honey!",
        "Record the story and play it back every time they start telling it. Include a laugh track for extra spice.",
        "Replace all toilet paper with paper towels. When they complain, act surprised like it's always been that way.",
        "Send them a bill for your time, itemized by each notification sound you heard.",
        "Tell them you'd love to stay friends - you need someone to help you move next weekend anyway.",
        "Start a cooking YouTube channel featuring their disasters. Call it 'Kitchen Nightmares: Home Edition'.",
        "Send them an invoice for your wasted evenings. Include a bad date tax.",
        "Start bringing extremely spicy lunches. Some lessons need to burn twice.",
        "Show her his dating profile where he lists his occupation as 'professional boyfriend'."
    ],
    'funny': [
        "Own it! Start calling everyone at work 'mom' now. Create confusion. Assert dominance.",
        "Time to move to a new country and start a new life as a shepherd in the mountains.",
        "Tell them your phone was possessed by the ghost of romance past.",
        "Clearly the universe is telling you you're soulmates. Plan the wedding immediately!",
        "Celebrate your mutual forgetfulness! It's like having two anniversaries for the price of none.",
        "Start mixing up Star Wars and Star Trek quotes. See how long until they notice.",
        "Tell them you're practicing for your secret career as a backup dancer.",
        "YouTube 'wine tasting' and pray no one notices you're drinking grape juice.",
        "Gradually transition to a different fake accent every week. Keep them guessing.",
        "Tell them you're preparing for hibernation. It's totally natural."
    ],
    'revenge': [
        "Start a GoFundMe for their 'financial literacy education'. Share it everywhere.",
        "Excel at your job so hard they have to report to you one day.",
        "Park perfectly across two spots. Assert dominance. Become ungovernable.",
        "Replace the contents with tofu. Gaslight them into thinking they never liked meat.",
        "Subtly move everything in their room 2 inches to the left. Watch chaos unfold.",
        "Start playing baby shark at 6AM. Call it your 'morning meditation'.",
        "Document everything. Build your case. Rise above. Then become their boss.",
        "Make your version better. Success is the best revenge.",
        "Post amazing photos of you living your best life. Tag everyone except them.",
        "'Accidentally' tag them in every cringe couple post you see."
    ],
    'moody': [
        "Because hearts are complex and feelings don't come with manuals.",
        "Love is like the ocean - deep, mysterious, and sometimes you get stung by jellyfish.",
        "People are like seasons - always changing, rarely predictable.",
        "Loneliness is the echo of our unspoken thoughts in an empty room.",
        "We're all just trying to write new stories with old habits.",
        "Missing someone toxic is like craving sugar - your heart wants what hurts it.",
        "Good things end so better things can begin, but the transition is always stormy.",
        "Maybe we're all meant to be alone, just together.",
        "Words are heavy, and some people's shoulders aren't strong enough to carry them.",
        "Heartbreak leaves scars that become stories of survival."
    ],
    'wholesome': [
        "Leave little notes of appreciation where they'll find them throughout the day.",
        "Create a jar of 365 reasons why they make you smile.",
        "Be the friend who remembers the small details and celebrates their victories.",
        "Actions speak louder than words - show love through small, consistent gestures.",
        "Sometimes just being there and listening is the best support we can offer.",
        "Trust is built in small moments of keeping your word and choosing kindness.",
        "Create family traditions that celebrate your unique bond.",
        "Join groups that share your interests and approach others with openness.",
        "Schedule regular virtual coffee dates and send care packages.",
        "Start each day by listing three things you love about yourself."
    ]
}

def seed_database():
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    cursor = conn.cursor()

    # Create users
    user_ids = []
    for username in SAMPLE_USERS:
        cursor.execute("""
            INSERT INTO user (username, password_hash)
            VALUES (%s, %s)
        """, (username, generate_password_hash(f"{username}123")))
        user_ids.append(cursor.lastrowid)

    # Create advice entries
    for mode in SAMPLE_QUESTIONS:
        for i in range(len(SAMPLE_QUESTIONS[mode])):
            # Random user
            user_id = random.choice(user_ids)
            
            # Random date within last 30 days
            random_date = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Random number of likes and dislikes
            likes = random.randint(0, 1000)
            dislikes = random.randint(0, 200)

            cursor.execute("""
                INSERT INTO advice (question, response, mode, likes, dislikes, created_at, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                SAMPLE_QUESTIONS[mode][i],
                SAMPLE_RESPONSES[mode][i],
                mode,
                likes,
                dislikes,
                random_date,
                user_id
            ))

            # Add some random votes
            advice_id = cursor.lastrowid
            for _ in range(likes + dislikes):
                voter_id = random.choice(user_ids)
                vote_type = 'like' if random.random() < (likes/(likes + dislikes)) else 'dislike'
                try:
                    cursor.execute("""
                        INSERT INTO user_vote (user_id, advice_id, vote_type)
                        VALUES (%s, %s, %s)
                    """, (voter_id, advice_id, vote_type))
                except mysql.connector.IntegrityError:
                    # Skip if user already voted
                    continue

    conn.commit()
    cursor.close()
    conn.close()
    print("Database has been seeded with sample data successfully!")

if __name__ == "__main__":
    seed_database() 