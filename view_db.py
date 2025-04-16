from app import app, User, Advice, UserVote
from datetime import datetime

def view_database():
    with app.app_context():
        print("\n=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}")

        print("\n=== Advice ===")
        advices = Advice.query.all()
        for advice in advices:
            print(f"\nID: {advice.id}")
            print(f"Question: {advice.question}")
            print(f"Savage Response: {advice.savage_response}")
            print(f"Likes: {advice.likes}, Dislikes: {advice.dislikes}")
            print(f"Created at: {advice.created_at}")
            print(f"User ID: {advice.user_id}")

        print("\n=== User Votes ===")
        votes = UserVote.query.all()
        for vote in votes:
            print(f"User ID: {vote.user_id}, Advice ID: {vote.advice_id}, Vote: {'Like' if vote.vote else 'Dislike'}")

if __name__ == "__main__":
    view_database() 