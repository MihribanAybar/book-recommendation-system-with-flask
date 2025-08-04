from app import app, db, FavoriteBook

def view_favorites():
    with app.app_context():
        favorites = FavoriteBook.query.all()
        for favorite in favorites:
            print(f"User ID: {favorite.user_id}, Book Title: {favorite.book_title}, Author: {favorite.author}")

if __name__ == "__main__":
    view_favorites()