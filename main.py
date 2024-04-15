"""Программа для управления клиентами на Python"""

import psycopg2

def get_cursor(conn):
    """Создает и возвращает объект cursor,
    который используется для взаимодействия
    с подключением к базе данных"""
    cur = conn.cursor()
    return cur

def create_table(conn):
    """Функция, создающая структуру БД (таблицы)"""
    cur = get_cursor(conn)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Client(
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(25) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        email VARCHAR(60) NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Phone(
    id SERIAL PRIMARY KEY,
    number_phone BIGINT UNIQUE,
    client_id INTEGER NOT NULL REFERENCES Client(client_id)
    );
    """)
    conn.commit()
    return 'Table created'

def add_new_client(conn, first_name, last_name, email):
    """Функция, позволяющая добавить нового клиента"""
    try:
        cur = get_cursor(conn)
        cur.execute("""
        INSERT INTO Client(first_name, last_name, email)
        VALUES (%s, %s, %s) RETURNING client_id;
        """, (first_name, last_name, email)
        )
        print(f'New client with id {cur.fetchone()[0]} added')
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        return ('This client already exists', e)

def add_number_phone(conn, phone, client_id):
    """Функция, позволяющая добавить
    телефон для существующего клиента"""
    try:
        cur = get_cursor(conn)
        cur.execute("""
        INSERT INTO Phone(number_phone, client_id)
        VALUES (%s, %s);
        """, (phone, client_id)
        )
        conn.commit()
        print(f"New number phone client's with id {client_id} added")
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        return ('This number phone already exists', e)

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phone=None):
    """Функция, позволяющая изменить данные о клиенте"""
    cur = get_cursor(conn)
    if first_name is not None:
        cur.execute("""
        UPDATE Client
        SET first_name = %s
        WHERE client_id = %s;
        """, (first_name, client_id)
        )
        conn.commit()
        print('First name changed')
    elif last_name is not None:
        cur.execute("""
        UPDATE Client
        SET last_name = %s
        WHERE client_id = %s;
        """, (last_name, client_id)
        )
        conn.commit()
        print('Last name changed')
    elif email is not None:
        cur.execute("""
        UPDATE Client
        SET email = %s
        WHERE client_id = %s;
        """, (email, client_id)
        )
        conn.commit()
        print('Email changed')
    else:
        cur.exeute("""
        UPDATE Phone
        SET number_phone = %s
        WHERE client_id = %s;
        """, (phone, client_id)
        )
        conn.commit()
        print('Number phone changed')

def delete_phone(conn, client_id, phone):
    """Функция, позволяющая удалить
    телефон для существующего клиента"""
    cur = get_cursor(conn)
    cur.execute("""
    DELETE FROM Phone
    WHERE client_id = %s AND number_phone = %s;
    """, (client_id, phone)
    )
    conn.commit()
    return f'The phone number {phone} of the client with id {client_id} was deleted'

def delete_client(conn, client_id, first_name):
    """Функция, позволяющая удалить существующего клиента"""
    cur = get_cursor(conn)
    cur.execute("""
    DELETE FROM Phone
    WHERE client_id = %s;
    """, (client_id, )
    )
    cur.execute("""
    DELETE FROM Client
    WHERE client_id = %s AND first_name = %s;
    """, (client_id, first_name, )
    )
    conn.commit()
    return f'The client with id {client_id} and name {first_name} was deleted'

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    """Функция, позволяющая найти клиента
    по его данным: имени, фамилии, email
    или телефону"""
    cur = get_cursor(conn)
    if phone is None:
        cur.execute("""
        SELECT * FROM Client
        WHERE first_name LIKE %s AND last_name LIKE %s AND email LIKE %s;
        """, (first_name, last_name, email)
        )
        return cur.fetchone()[0]
    else:
        cur.execute("""
        SELECT client_id From Phone
        WHERE number_phone LIKE %s;
        """, (phone, )
        )
        return cur.fetchone()[0]

if __name__ == '__main__':
    with psycopg2.connect(database='client_db', user='postgres', password='*********') as conn:
        create_table(conn)
        add_new_client(conn, 'Alexey', 'Kuzmin', 'kuz@example.com')
        add_new_client(conn, 'Leo', 'Levin', 'lenin@examle.com')
        add_number_phone(conn, 89002223322, 1)
        add_number_phone(conn, 83520451213, 2)
        change_client(conn, 1, email='kuzmin@example.com')
        delete_phone(conn, 1, 89002223322)
        delete_client(conn, 1, 'Alexey')
        find_client(conn, 'Alexey')
    conn.close()
