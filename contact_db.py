import sqlite3

def view_contacts():
    conn = sqlite3.connect('contact.db')
    c = conn.cursor()
    c.execute('SELECT * FROM contacts')
    contacts = c.fetchall()
    conn.close()
    
    for contact in contacts:
        print(f"Name: {contact[0]}, Email: {contact[2]}, Message: {contact[1]}")

if __name__ == "__main__":
    view_contacts()
