import PySimpleGUI as sg
import psycopg

def edit_contract(contract_id, new_details):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        update_query = "UPDATE contracts SET details = %s WHERE id = %s"
        cursor.execute(update_query, (new_details, contract_id))
        connection.commit()
        sg.popup('Контракт успішно оновлено')
    except Exception as e:
        sg.popup(f"Помилка при оновленні контракту: {e}")
    finally:
        cursor.close()
        connection.close()

def cancel_contract(contract_id):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        delete_query = "DELETE FROM contracts WHERE id = %s"
        cursor.execute(delete_query, (contract_id,))
        connection.commit()
        sg.popup('Контракт успішно скасовано')
    except Exception as e:
        sg.popup(f"Помилка при скасуванні контракту: {e}")
    finally:
        cursor.close()
        connection.close()

def view_sales_data():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM sales"
        cursor.execute(select_query)
        sales_data = cursor.fetchall()
        sg.popup_scrolled('Дані про продажі', sales_data)
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних про продажі: {e}")
    finally:
        cursor.close()
        connection.close()

def add_employee(username, password, firstname, lastname, role):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        create_user_query = f"CREATE USER {username} WITH PASSWORD '{password}';"
        cursor.execute(create_user_query)
        insert_query = "INSERT INTO employees (username, first_name, last_name, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, firstname, lastname, role))
        connection.commit()
        sg.popup('Співробітника успішно додано')
    except Exception as e:
        sg.popup(f"Помилка при додаванні співробітника: {e}")
    finally:
        cursor.close()
        connection.close()

def remove_employee(username):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        delete_user_query = f"DROP USER {username};"
        cursor.execute(delete_user_query)
        delete_employee_query = "DELETE FROM employees WHERE username = %s"
        cursor.execute(delete_employee_query, (username,))
        connection.commit()
        sg.popup('Співробітника успішно видалено')
    except Exception as e:
        sg.popup(f"Помилка при видаленні співробітника: {e}")
    finally:
        cursor.close()
        connection.close()

def create_director_window():
    layout = [
        [sg.Button('Редагувати контракт'), sg.Button('Скасувати контракт')],
        [sg.Button('Переглянути дані продажів')],
        [sg.Button('Додати співробітника'), sg.Button('Видалити співробітника')],
        [sg.Button('Вихід')]
    ]
    window = sg.Window('Вікно Директора', layout)
    return window

def director_main():
    window = create_director_window()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break
        elif event == 'Редагувати контракт':
            contract_id = sg.popup_get_text('Введіть ID контракту для редагування')
            new_details = sg.popup_get_text('Введіть нові деталі контракту')
            edit_contract(contract_id, new_details)
        elif event == 'Скасувати контракт':
            contract_id = sg.popup_get_text('Введіть ID контракту для скасування')
            cancel_contract(contract_id)
        elif event == 'Переглянути дані продажів':
            view_sales_data()
        elif event == 'Додати співробітника':
            username = sg.popup_get_text('Введіть ім\'я користувача')
            password = sg.popup_get_text('Введіть пароль', password_char='*')
            firstname = sg.popup_get_text('Введіть ім\'я')
            lastname = sg.popup_get_text('Введіть прізвище')
            role = sg.popup_get_text('Введіть роль')
            add_employee(username, password, firstname, lastname, role)
        elif event == 'Видалити співробітника':
            username = sg.popup_get_text('Введіть ім\'я користувача співробітника для видалення')
            remove_employee(username)

    window.close()

if __name__ == '__main__':
    director_main()
