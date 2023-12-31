import sqlite3


database = sqlite3.connect('wallpapers.db')
cursor = database.cursor()


cursor.executescript('''
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS categories;

CREATE TABLE IF NOT EXISTS categories(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(20) UNIQUE
);

CREATE TABLE IF NOT EXISTS images(
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_link TEXT UNIQUE,
    category_id INTEGER REFERENCES categories(category_id)
);
''')
database.commit()
database.close()


