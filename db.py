import settings
import psycopg2
from datetime import date

def connect():
    conn = psycopg2.connect(
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.HOST, 
        port=settings.PORT)

    cur = conn.cursor()

    return conn, cur

def create_new_user(first_name: str, last_name: str, email: str, phone_number: str, birth_date: date, accepted_privacy_policy: bool) -> bool:
    conn, cur = connect()
    
    try:    
        cur.execute('''
            INSERT INTO db_user (first_name, last_name, email, phone, birth_date, accepted_privacy_policy, joined)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        ''', (first_name, last_name, email, phone_number, birth_date, accepted_privacy_policy, date.today()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        cur.close()
        conn.close()
        return False
    
def get_user_by_phone(value: str):
    conn, cur = connect()

    cur.execute('SELECT * FROM db_user WHERE phone = %s', (value,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_user_by_email(value: str):
    conn, cur = connect()

    cur.execute('SELECT * FROM db_user WHERE email = %s', (value,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def get_categories():
    conn, cur = connect()
    
    cur.execute('''
    SELECT c.category, p.*
        FROM db_product_category pc
        JOIN db_product p ON pc.product_id = p.id
        JOIN db_category c ON pc.category_id = c.id;
    ''')
    categories = cur.fetchall()

    cur.close()
    conn.close()
    return categories

def update_user_by_id(first_name: str, last_name: str, email: str, id: int):
    conn, cur = connect()

    try:
        cur.execute('''
            UPDATE db_user
            SET first_name = %s,
                last_name = %s,
                email = %s
            WHERE id = %s;
        ''', (first_name, last_name, email, id))

        conn.commit()
        cur.close()
        conn.close()
        return True 
    except:
        cur.close()
        conn.close()
        return False

if __name__ == '__main__':
    conn, cur = connect()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_product (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200),
        description TEXT,
        article INTEGER,
        size VARCHAR(500),
        weight INTEGER,
        price INTEGER,
        discount INTEGER
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_user (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        phone VARCHAR(20) UNIQUE,
        birth_date DATE,
        accepted_privacy_policy BOOLEAN DEFAULT FALSE,
        joined DATE
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_user_cart (
        user_id INTEGER REFERENCES db_user(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES db_product(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, product_id)
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_favorite_product (
        user_id INTEGER REFERENCES db_user(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES db_product(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, product_id)
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_product_bought (
        user_id INTEGER REFERENCES db_user(id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES db_product(id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, product_id)
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_category (
        id SERIAL PRIMARY KEY,
        category TEXT          
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_product_category (
        product_id INTEGER REFERENCES db_product(id) ON DELETE CASCADE,
        category_id INTEGER REFERENCES db_category(id) ON DELETE CASCADE,
        PRIMARY KEY (product_id, category_id)          
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_image (
        id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES db_product(id),
        url TEXT
    );''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS db_comment (
        id SERIAL PRIMARY KEY,
        email VARCHAR(100),
        phone VARCHAR(20),
        comment TEXT,
        rating FLOAT,
        product_id INTEGER REFERENCES db_product(id)
    );''')

    conn.commit()
    cur.close()
    conn.close()