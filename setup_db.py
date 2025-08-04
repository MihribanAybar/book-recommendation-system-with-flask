from app import app, db  # app.py dosyasından app ve db örneklerini içe aktarın
from models import User, FavoriteBook  # Modellerinizi içe aktarın

""" conn = sqlite3.connect('contact.db')
c = conn.cursor()

c.execute('''
          CREATE TABLE contacts
          (id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT NOT NULL,
          message TEXT NOT NULL)
          ''')

conn.commit()
conn.close() """

# Veritabanı oluşturma fonksiyonu
def create_database():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_database()