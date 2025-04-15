import database

conn = database.conn_db()
cur = conn.cursor()

def task_add(name, description):
    request_task = f'INSERT INTO tasks (task_name, task_description) VALUES ("{name}", "{description}")'
    try:
        cur.execute(request_task)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close() 
