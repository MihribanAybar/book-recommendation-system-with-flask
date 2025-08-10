from app import app, db, User, FavoriteBook

def view_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"Username: {user.username}, Password: {user.password}")

if __name__ == "__main__":
    view_users()
