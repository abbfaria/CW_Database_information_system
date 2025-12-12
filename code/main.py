import PySimpleGUI as sg
import psycopg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import date

user_db_config = {
        'dbname': 'publishing_house',
        'user': 'wald',
        'password': 'wald',
        'host': 'localhost',
        'port': '5432'
        }

# Функція для перевірки імені користувача та пароля
def authenticate_user(username, password):
    try:
        # Налаштування підключення з даними користувача
        user_db_config['user'] = username
        user_db_config['password'] = password

        # Спроба підключитися до бази даних з цими обліковими даними
        connection = psycopg.connect(**user_db_config)
        # connection.close()
        return True
    except Exception as e:
        sg.popup('Неправильне ім\'я користувача або пароль')
        return False

# Функція для створення нового користувача
def create_client(username, password, firstname, lastname, phonenumber, birthday):
    try:
        # Підключення до бази даних
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()

        # Створення нового клієнта
        create_client_query = f"CREATE USER {username} WITH PASSWORD '{password}'"
        cursor.execute(create_client_query)

        # Додавання користувача до таблиці users з датою народження
        insert_query = "INSERT INTO auth_info (login, first_name, last_name, phone_number, birthday) VALUES  (%s, %s, %s, %s, %s)"
        add_client_query = "INSERT INTO client (login, purchases, status) VALUES (%s, %s, %s)"
        grant_r_client_query = f"GRANT pg_read_all_data TO {username}"
        grant_w_client_query = f"GRANT pg_write_all_data TO {username}"
        cursor.execute(grant_r_client_query)
        cursor.execute(grant_w_client_query)
        cursor.execute(insert_query, (username, firstname, lastname, phonenumber, birthday))
        cursor.execute(add_client_query, (username, 0, 'new'))
        connection.commit()
        sg.popup('Користувач успішно створений')
        return True
    except Exception as e:
        sg.popup(f"Помилка при створенні користувача: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

# Функція для створення вікна реєстрації
def create_registration_window():
    layout = [
            [sg.Text('Ім\'я користувача', size=(20,1)), sg.InputText(key='-REG_USERNAME-')],
            [sg.Text('Пароль', size=(20,1)), sg.InputText(password_char='*', key='-REG_PASSWORD-')],
            [sg.Text('Ім\'я', size=(20,1)), sg.InputText(key='-REG_FIRSTNAME-')],
            [sg.Text('Призвище', size=(20,1)), sg.InputText(key='-REG_LASTNAME-')],
            [sg.Text('Телефон', size=(20,1)), sg.InputText(key='-REG_PHONENUMBER-')],
            [sg.Text('Дата народження', size=(20,1)), sg.InputText(key='-REG_BIRTHDAY-')],
            [sg.Button('Зареєструватися', size=(20,1)), sg.Button('Назад')]
            ]

    window = sg.Window('Реєстрація', layout)
    return window

# Функція для створення вікна авторизації
def create_login_window():
    layout = [
            [sg.Text('Ім\'я користувача', size=(20,1)), sg.InputText(key='-USERNAME-')],
            [sg.Text('Пароль', size=(20,1)), sg.InputText(password_char='*', key='-PASSWORD-')],
            [sg.Button('Увійти', size=(20,1)), sg.Button('Реєстрація'), sg.Button('Вихід')]
            ]
    window = sg.Window('Авторизація', layout)
    return window

# Функція для перевірки ролі користувача
def get_user_role(username, password):
    try:
        # Підключення до бази даних
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        user_db_config['user'] = username
        user_db_config['password'] = password
        query = "SELECT position FROM worker WHERE login = %s";
        cursor.execute(query, (username,))
        connection.commit()
        role = cursor.fetchone()[0]
        return role
    except Exception as e:
        role = 'client'
        return role
    finally:
        cursor.close()
        connection.close()

# Функція створення головного вікна
def create_main_window(user_role):
    button_size = (30, 1)  # Встановлюємо однаковий розмір для всіх кнопок
    layout = [
        [sg.Text('Ласкаво просимо!', size=button_size, font=('Helvetica', 25))],
        [sg.Text('Ви успішно авторизувалися.')]
    ]

    if user_role == 'director':
        layout.append([sg.Button('Вікно директора', size=button_size)])
    if user_role == 'administrator':
        layout.append([sg.Button('Вікно адміністратора', size=button_size)])
    if user_role == 'editor':
        layout.append([sg.Button('Вікно редактора', size=button_size)])
    if user_role == 'client':
        layout.append([sg.Button('Вікно клієнта', size=button_size)])

    layout.append([sg.Button('Вихід', size=button_size)])


    window = sg.Window('Головне вікно', layout)
    return window

### Admin Window ######

def create_admin_window():
    button_size = (30, 1)  # Встановлюємо однаковий розмір для всіх кнопок
    layout = [
        [sg.Button('Редагувати контракт', size=button_size)],
        [sg.Button('Скасувати контракт', size=button_size)],
        [sg.Button('Додати співробітника', size=button_size)],
        [sg.Button('Редагувати співробітника', size=button_size)],
        [sg.Button('Вихід', size=button_size)]
    ]
    window = sg.Window('Панель адміністратора', layout)
    return window


def get_contracts():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM contract"
        cursor.execute(select_query)
        contracts = cursor.fetchall()
        return contracts
    except Exception as e:
        sg.popup(f"Помилка при отриманні контрактів: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def edit_contract_window():
    contracts = get_contracts()
    
    layout = [
        [sg.Text('Введіть ID контракту для редагування')],
        [sg.InputText(key='-CONTRACT_ID-')],
        [sg.Button('Редагувати контракт'), sg.Button('Відміна')],
        [sg.Text('Контракти')],
        [sg.Table(values=[list(row) for row in contracts], headings=['ID Контракту', 'ID Працівника', 'ID Матеріалу', 'Тираж', 'Статус', 'Дата зміни', 'Попередній статус'], auto_size_columns=True)],
    ]
    window = sg.Window('Скасування контракту', layout)

    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break
        
        if event == 'Редагувати контракт':
            contract_id = values['-CONTRACT_ID-']
            try:
                edit_contract(contract_id)
                contracts = get_contracts()
                window['-CONTRACT_LIST-'].update(values=[f"ID: {contract[0]}, Працівник: {contract[1]}, Матеріал: {contract[2]}, Тираж: {contract[3]}, Статус: {contract[4]}, Дата зміни: {contract[5]}, Попередній статус: {contract[6]}" for contract in contracts])
            except ValueError:
                sg.popup('Помилка: ID контракту має бути числом')
            except Exception as e:
                sg.popup(f"Помилка при скасуванні контракту: {e}")
    window.close()

def edit_contract(contract_id):
    today = date.today()
    # Отримуємо дані контракту за заданим ID
    contract = None
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM contract WHERE contract_id = %s"
        cursor.execute(select_query, (contract_id,))
        contract = cursor.fetchone()
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних контракту: {e}")
    finally:
        cursor.close()
        connection.close()

    if not contract:
        sg.popup('Контракт з таким ID не знайдено')
        return

    # Плейсхолдери для полів введення
    placeholders = {
        '-CONTRACT_ID-': str(contract[0]),
        '-WORKER_ID-': str(contract[1]),
        '-MATERIAL_ID-': str(contract[2]),
        '-PLANNED_CIRCULATION-': str(contract[3]),
        '-STATUS-': contract[4],
        '-LAST_CHANGED_DATE-': str(contract[5]),
        '-PREVIOUS_STATUS-': contract[6]
    }
    
    layout = [
        [sg.Text('ID контракту', size=(20, 1)), sg.InputText(placeholders['-CONTRACT_ID-'], key='-CONTRACT_ID-', readonly=True)],
        [sg.Text('ID працівника', size=(20, 1)), sg.InputText(placeholders['-WORKER_ID-'], key='-WORKER_ID-')],
        [sg.Text('ID матеріалу', size=(20, 1)), sg.InputText(placeholders['-MATERIAL_ID-'], key='-MATERIAL_ID-')],
        [sg.Text('Планований тираж', size=(20, 1)), sg.InputText(placeholders['-PLANNED_CIRCULATION-'], key='-PLANNED_CIRCULATION-')],
        [sg.Text('Статус', size=(20, 1)), sg.InputText(placeholders['-STATUS-'], key='-STATUS-')],
        [sg.Text('Дата зміни статусу', size=(20, 1)), sg.InputText(placeholders['-LAST_CHANGED_DATE-'], key='-LAST_CHANGED_DATE-', readonly=True)],
        [sg.Text('Попередній статус', size=(20, 1)), sg.InputText(placeholders['-PREVIOUS_STATUS-'], key='-PREVIOUS_STATUS-', readonly=True)],
        [sg.Button('Оновити контракт'), sg.Button('Відміна')]
    ]

    window = sg.Window('Редагування контракту', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Оновити контракт':
            try:
                contract_id = int(values['-CONTRACT_ID-'])
                worker_id = int(values['-WORKER_ID-'])
                material_id = int(values['-MATERIAL_ID-'])
                planed_circulation = int(values['-PLANNED_CIRCULATION-'])
                status = values['-STATUS-']
                last_changed_date = today.strftime("%m.%d.%Y")
                previous_status = contract[4]
                if update_contract(contract_id, worker_id, material_id, planed_circulation, status, last_changed_date, previous_status):
                    break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def update_contract(contract_id, worker_id, material_id, planed_circulation, status, last_changed_date, previous_status):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        update_query = """
        UPDATE contract 
        SET worker_id = %s, material_id = %s, planed_circulation = %s, status = %s, last_changed_date = %s, previous_status = %s
        WHERE contract_id = %s
        """
        cursor.execute(update_query, (worker_id, material_id, planed_circulation, status, last_changed_date, previous_status, contract_id))
        connection.commit()
        sg.popup('Контракт успішно оновлено')
        return True
    except Exception as e:
        sg.popup(f"Помилка при оновленні контракту: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def cancel_contract_window():
    contracts = get_contracts()
    
    layout = [
        [sg.Text('Введіть ID контракту для скасування')],
        [sg.InputText(key='-CONTRACT_ID-')],
        [sg.Button('Скасувати контракт'), sg.Button('Відміна')],
        [sg.Text('Контракти')],
        [sg.Table(values=[list(row) for row in contracts], headings=['ID Контракту', 'ID Працівника', 'ID Матеріалу', 'Тираж', 'Статус', 'Дата зміни', 'Попередній статус'], auto_size_columns=True)],
    ]
    window = sg.Window('Скасування контракту', layout)

    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break
        
        if event == 'Скасувати контракт':
            contract_id = values['-CONTRACT_ID-']
            try:
                contract_id = int(contract_id)
                connection = psycopg.connect(**user_db_config)
                cursor = connection.cursor()
                delete_query = "DELETE FROM contract WHERE contract_id = %s"
                cursor.execute(delete_query, (contract_id,))
                connection.commit()
                sg.popup('Контракт успішно скасовано')
                contracts = get_contracts()  # Оновлюємо список контрактів після скасування
                window['-CONTRACT_LIST-'].update(values=[f"ID: {contract[0]}, Працівник: {contract[1]}, Матеріал: {contract[2]}, Тираж: {contract[3]}, Статус: {contract[4]}, Дата зміни: {contract[5]}, Попередній статус: {contract[6]}" for contract in contracts])
            except ValueError:
                sg.popup('Помилка: ID контракту має бути числом')
            except Exception as e:
                sg.popup(f"Помилка при скасуванні контракту: {e}")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
    
    window.close()

def add_employee_to_db(auth_info, worker_info):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        
        insert_auth_info_query = """
        INSERT INTO auth_info (login, first_name, last_name, phone_number, birthday) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_auth_info_query, auth_info)
        
        insert_worker_query = """
        INSERT INTO worker (login, position, status) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_worker_query, worker_info)
        connection.commit()
        if worker_info[2] == 'administrator':
            grant_role_query = "ALTER USER %s CREATEROLE"
            cursor.execute(grant_role_query, (worker_info[1],))   
            cursor.commit()
        
        sg.popup('Співробітника успішно додано')
    except Exception as e:
        sg.popup(f"Помилка при додаванні співробітника: {e}")
    finally:
        cursor.close()
        connection.close()

def add_employee_window():
    layout = [
        [sg.Text('Логін', size=(20, 1)), sg.InputText(key='-LOGIN-')],
        [sg.Text('Ім\'я', size=(20, 1)), sg.InputText(key='-FIRST_NAME-')],
        [sg.Text('Прізвище', size=(20, 1)), sg.InputText(key='-LAST_NAME-')],
        [sg.Text('Номер телефону', size=(20, 1)), sg.InputText(key='-PHONE_NUMBER-')],
        [sg.Text('Дата народження', size=(20, 1)), sg.InputText(key='-BIRTHDAY-')],
        [sg.Text('Позиція', size=(20, 1)), sg.Combo(['administrator', 'editor', 'director'], key='-POSITION-')],
        [sg.Button('Додати співробітника'), sg.Button('Відміна')]
    ]
    window = sg.Window('Додавання співробітника', layout)

    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break
        
        if event == 'Додати співробітника':
            try:
                login = values['-LOGIN-']
                first_name = values['-FIRST_NAME-']
                last_name = values['-LAST_NAME-']
                phone_number = values['-PHONE_NUMBER-']
                birthday = values['-BIRTHDAY-']
                position = values['-POSITION-']
                status = 'works'
                auth_info = (login, first_name, last_name, phone_number, birthday)
                worker_info = (login, position, status)
                add_employee_to_db(auth_info, worker_info)
                break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")
            except Exception as e:
                sg.popup(f"Помилка: {e}")
    
    window.close()

def get_employees():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = """
        SELECT w.worker_id, w.login, w.position, w.status, a.first_name, a.last_name, a.phone_number, a.birthday
        FROM worker w
        JOIN auth_info a ON w.login = a.login
        """
        cursor.execute(select_query)
        employees = cursor.fetchall()
        return employees
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних співробітників: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_employee(worker_id, login, position, status, first_name, last_name, phone_number, birthday):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        
        update_worker_query = """
        UPDATE worker 
        SET position = %s, status = %s
        WHERE worker_id = %s
        """
        cursor.execute(update_worker_query, (position, status, worker_id))
        
        update_auth_info_query = """
        UPDATE auth_info
        SET first_name = %s, last_name = %s, phone_number = %s, birthday = %s
        WHERE login = %s
        """
        cursor.execute(update_auth_info_query, (first_name, last_name, phone_number, birthday, login))
        
        connection.commit()
        sg.popup('Дані співробітника успішно оновлено')
        return True
    except Exception as e:
        sg.popup(f"Помилка при оновленні даних співробітника: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def edit_employee(login):
    # Отримуємо дані співробітника за заданим логіном
    employee = None
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = """
        SELECT w.worker_id, w.login, w.position, w.status, a.first_name, a.last_name, a.phone_number, a.birthday
        FROM worker w
        JOIN auth_info a ON w.login = a.login
        WHERE w.login = %s
        """
        cursor.execute(select_query, (login,))
        employee = cursor.fetchone()
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних співробітника: {e}")
    finally:
        cursor.close()
        connection.close()

    if not employee:
        sg.popup('Співробітник з таким логіном не знайдено')
        return

    # Плейсхолдери для полів введення
    placeholders = {
        '-WORKER_ID-': str(employee[0]),
        '-LOGIN-': employee[1],
        '-POSITION-': employee[2],
        '-STATUS-': employee[3],
        '-FIRST_NAME-': employee[4],
        '-LAST_NAME-': employee[5],
        '-PHONE_NUMBER-': employee[6],
        '-BIRTHDAY-': str(employee[7])
    }
    
    layout = [
        [sg.Text('ID працівника', size=(20, 1)), sg.InputText(placeholders['-WORKER_ID-'], key='-WORKER_ID-', readonly=True)],
        [sg.Text('Логін', size=(20, 1)), sg.InputText(placeholders['-LOGIN-'], key='-LOGIN-', readonly=True)],
        [sg.Text('Ім\'я', size=(20, 1)), sg.InputText(placeholders['-FIRST_NAME-'], key='-FIRST_NAME-')],
        [sg.Text('Прізвище', size=(20, 1)), sg.InputText(placeholders['-LAST_NAME-'], key='-LAST_NAME-')],
        [sg.Text('Номер телефону', size=(20, 1)), sg.InputText(placeholders['-PHONE_NUMBER-'], key='-PHONE_NUMBER-')],
        [sg.Text('Дата народження', size=(20, 1)), sg.InputText(placeholders['-BIRTHDAY-'], key='-BIRTHDAY-')],
        [sg.Text('Позиція', size=(20, 1)), sg.Combo(['administrator', 'editor', 'director'], key='-POSITION-')],
        [sg.Text('Статус', size=(20, 1)), sg.InputText(placeholders['-STATUS-'], key='-STATUS-')],
        [sg.Button('Оновити дані'), sg.Button('Відміна')]
    ]

    window = sg.Window('Редагування даних співробітника', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Оновити дані':
            try:
                worker_id = int(values['-WORKER_ID-'])
                login = values['-LOGIN-']
                first_name = values['-FIRST_NAME-']
                last_name = values['-LAST_NAME-']
                phone_number = values['-PHONE_NUMBER-']
                birthday = values['-BIRTHDAY-']
                position = values['-POSITION-']
                status = values['-STATUS-']

                if update_employee(worker_id, login, position, status, first_name, last_name, phone_number, birthday):
                    break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def edit_employee_window():
    employees = get_employees()
    
    layout = [
        [sg.Text('Введіть логін співробітника для редагування')],
        [sg.InputText(key='-LOGIN-')],
        [sg.Button('Редагувати співробітника'), sg.Button('Відміна')],
        [sg.Text('Співробітники')],
        [sg.Listbox(values=[f"Логін: {employee[1]}, Ім'я: {employee[4]}, Прізвище: {employee[5]}, Позиція: {employee[2]}, Статус: {employee[3]}, Номер телефону: {employee[6]}, Дата народження: {employee[7]}" for employee in employees], size=(100, 20), key='-EMPLOYEE_LIST-')]
#        [sg.Table(values=[list(row) for row in employees], headings=['Логін', 'Ім\'я', 'Прізвище', 'Позиція', 'Статус', 'Номер телефону', 'Дата народження'], auto_size_columns=True, key='-EMPLOYEE_LIST-')]
    ]
    window = sg.Window('Редагування співробітника', layout)

    while True:
        event, values = window.read()
        
        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break
        
        if event == 'Редагувати співробітника':
            login = values['-LOGIN-']
            edit_employee(login)
            employees = get_employees()  # Оновлюємо список співробітників після редагування
            window['-EMPLOYEE_LIST-'].update(values=[f"Логін: {employee[1]}, Ім'я: {employee[4]}, Прізвище: {employee[5]}, Позиція: {employee[2]}, Статус: {employee[3]}, Номер телефону: {employee[6]}, Дата народження: {employee[7]}" for employee in employees])

    window.close()

def admin_main():
    window = create_admin_window()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break
        elif event == 'Редагувати контракт':
            edit_contract_window()
        elif event == 'Скасувати контракт':
            cancel_contract_window()
        elif event == 'Додати співробітника':
            add_employee_window()
        elif event == 'Редагувати співробітника':
            edit_employee_window()
    window.close()

### Editor Window ######

def create_editor_window():
    button_size = (30, 1)  # Встановлюємо однаковий розмір для всіх кнопок
    layout = [
        [sg.Button('Створити контракт', size=button_size)],
        [sg.Button('Опублікувати матеріал', size=button_size)],
        [sg.Button('Редагувати запити', size=button_size)],
        [sg.Button('Вихід', size=button_size)]
    ]
    window = sg.Window('Панель редактора', layout)
    return window

def editor_main():
    window = create_editor_window()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break
        elif event == 'Створити контракт':
            create_contract_window()
        elif event == 'Опублікувати матеріал':
            publicate_material_window()
        elif event == 'Редагувати запити':
            edit_requests_window()
    window.close()

def create_contract(title, author, genre, form, age_restriction, planed_circulation):
    today = date.today()
    login = user_db_config['user']
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT worker_id FROM worker WHERE login =%s"
        cursor.execute(select_query, (login,))
        result = cursor.fetchone()
        
        if result is None:
            sg.popup('Помилка: не знайдено користувача з таким логіном')
            return

        editor_id = result[0]
        insert_material_query = """
        INSERT INTO material_info (title, author, genre, form, age_restriction) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_material_query, (title, author, genre, form, age_restriction))
        connection.commit()
        select_query = "SELECT material_id FROM material_info WHERE title = %s AND author = %s"
        cursor.execute(select_query, (title, author,))
        result = cursor.fetchone()
        material_id = result[0]
        insert_contract_query = """
        INSERT INTO contract (worker_id, material_id, planed_circulation, status, last_changed_date, previous_status) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        last_changed_date = today.strftime("%m.%d.%Y")
        status = 'processing'
        previous_status = None
        cursor.execute(insert_contract_query, (editor_id, material_id, planed_circulation, status, last_changed_date, previous_status))
        connection.commit()
        sg.popup('Контракт успішно створено')
    except Exception as e:
        sg.popup(f"Помилка при створенні контракту: {e}")
    finally:
        cursor.close()
        connection.close()

def create_contract_window():
    layout = [
        [sg.Text('Назва', size=(20, 1)), sg.InputText(key='-TITLE-')],
        [sg.Text('Автор', size=(20, 1)), sg.InputText(key='-AUTHOR-')],
        [sg.Text('Жанр', size=(20, 1)), sg.Combo(['fiction', 'romance', 'scifiction', 'detective', 'adventure', 'for children', 'history', 'educational', 'news', 'magazine'], key='-GENRE-')],
        [sg.Text('Тип матеріалу', size=(20, 1)), sg.Combo(['paper book', 'electronic book', 'audio book', 'news', 'magazine'], key='-FORM-')],
        [sg.Text('Вікове обмеження', size=(20, 1)), sg.InputText(key='-AGE_RESTRICTION-')],
        [sg.Text('Тираж', size=(20, 1)), sg.InputText(key='-PLANNED_CIRCULATION-')],
        [sg.Button('Створити контракт'), sg.Button('Відміна')]
    ]
    window = sg.Window('Створення контракту', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break
        if event == 'Створити контракт':
            title = values['-TITLE-']
            author = values['-AUTHOR-']
            genre = values['-GENRE-']
            form = values['-FORM-']
            age_restriction = int(values['-AGE_RESTRICTION-'])
            planed_circulation = int(values['-PLANNED_CIRCULATION-'])
            create_contract(title, author, genre, form, age_restriction, planed_circulation)
    window.close()

def get_requests():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM request"
        cursor.execute(select_query)
        requests = cursor.fetchall()
        return requests
    except Exception as e:
        sg.popup(f"Помилка при отриманні запитів: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def update_request_status(request_id, status):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        update_query = "UPDATE request SET status = %s WHERE request_id = %s"
        cursor.execute(update_query, (status, request_id))
        connection.commit()
        sg.popup('Статус запиту успішно оновлено')
        return True
    except Exception as e:
        sg.popup(f"Помилка при оновленні статусу запиту: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def edit_request(request_id):
    # Отримуємо дані запиту за заданим ID
    request = None
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM request WHERE request_id = %s"
        cursor.execute(select_query, (request_id,))
        request = cursor.fetchone()
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних запиту: {e}")
    finally:
        cursor.close()
        connection.close()

    if not request:
        sg.popup('Запит з таким ID не знайдено')
        return

    # Плейсхолдери для полів введення
    placeholders = {
        '-REQUEST_ID-': str(request[0]),
        '-CLIENT_ID-': str(request[1]),
        '-TITLE-': request[2],
        '-AUTHOR-': request[3],
        '-COMMENT-': request[5]
    }
    
    layout = [
        [sg.Text('ID запиту', size=(20, 1)), sg.InputText(placeholders['-REQUEST_ID-'], key='-REQUEST_ID-', readonly=True)],
        [sg.Text('ID клієнта', size=(20, 1)), sg.InputText(placeholders['-CLIENT_ID-'], key='-CLIENT_ID-', readonly=True)],
        [sg.Text('Назва', size=(20, 1)), sg.InputText(placeholders['-TITLE-'], key='-TITLE-', readonly=True)],
        [sg.Text('Автор', size=(20, 1)), sg.InputText(placeholders['-AUTHOR-'], key='-AUTHOR-', readonly=True)],
        [sg.Text('Статус', size=(20, 1)), sg.Combo(['processing', 'accepted', 'annuled'], key='-STATUS-')],
        [sg.Text('Коментар', size=(20, 1)), sg.Multiline(placeholders['-COMMENT-'], key='-COMMENT-')],
        [sg.Button('Оновити статус'), sg.Button('Відміна')]
    ]

    window = sg.Window('Редагування запиту', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Оновити статус':
            try:
                status = values['-STATUS-']
                if update_request_status(request_id, status):
                    break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def edit_requests_window():
    requests = get_requests()
    
    layout = [
        [sg.Text('Оберіть запит для редагування')],
        [sg.InputText(key='-REQUEST_ID-', size=(20, 1))],
        [sg.Table(values=[list(row) for row in requests],
                  headings=['ID', 'Клієнт', 'Назва', 'Автор', 'Статус', 'Коментар'],
                  auto_size_columns=True, key='-REQUEST_LIST-', enable_events=True)],
        [sg.Button('Редагувати запит'), sg.Button('Відміна')]
    ]
    window = sg.Window('Редагування запиту', layout)

    while True:
        event, values = window.read()
        
        if event in (sg.WINDOW_CLOSED, 'Відміна'):
            break
        
        if event == 'Редагувати запит':
            request_id = values['-REQUEST_ID-'] or (values['-REQUEST_LIST-'][0][0] if values['-REQUEST_LIST-'] else None)
            if request_id:
                edit_request(request_id)
                window['-REQUEST_LIST-'].update(values=[list(row) for row in get_requests()])
    
    window.close()

# def edit_requests_window():
    # requests = get_requests()
    
    # layout = [
        # [sg.Text('Введіть ID запиту для редагування')],
        # [sg.InputText(key='-REQUEST_ID-')],
        # [sg.Button('Редагувати запит'), sg.Button('Відміна')],
        # [sg.Text('Запити')],
        # [sg.Listbox(values=[f"ID: {request[0]}, Клієнт: {request[1]}, Назва: {request[2]}, Автор: {request[3]}, Статус: {request[4]}, Коментар: {request[5]}" for request in requests], size=(100, 20), key='-REQUEST_LIST-')]
    # ]
    # window = sg.Window('Перегляд та редагування запитів', layout)

    # while True:
        # event, values = window.read()
        
        # if event == sg.WINDOW_CLOSED or event == 'Відміна':
            # break
        
        # if event == 'Редагувати запит':
            # request_id = values['-REQUEST_ID-']
            # try:
                # request_id = int(request_id)
                # edit_request(request_id)
                # requests = get_requests()  # Оновлюємо список запитів після редагування
                # window['-REQUEST_LIST-'].update(values=[f"ID: {request[0]}, Клієнт: {request[1]}, Назва: {request[2]}, Автор: {request[3]}, Статус: {request[4]}, Коментар: {request[5]}" for request in requests])
            # except ValueError:
                # sg.popup('Помилка: ID запиту має бути числом')

    # window.close()

### Client Window ######

def client_interface_window():
    materials = get_published_materials()
    layout = [
        [sg.Text('Опубліковані матеріали')],
#        [sg.Listbox(values=[f"Назва: {material[0]}, Автор: {material[1]}, Жанр: {material[2]}, Тип: {material[3]}, Вікове обмеження: {material[4]} Тираж: {material[5]}, Дата публікації: {material[6]}" for material in materials], size=(100, 20), key='-MATERIAL_LIST-')],        
        [sg.Table(values=[list(row) for row in materials], headings=['Назва', 'Автор', 'Жанр', 'Тип', 'Вікове обмеження', 'Тираж', 'Дата публікації'], auto_size_columns=True)],
        [sg.Button('Придбати'), sg.Button('Передивитися актуальні запити'), sg.Button('Вихід')] ]
    window = sg.Window('Інтерфейс клієнта', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break

        if event == 'Придбати':
            buy_material_window()
        if event == 'Передивитися актуальні запити':
            view_requests_window()

    window.close()

def buy_material_window():
    layout = [
        [sg.Text('Назва', size=(20, 1)), sg.InputText(key='-TITLE-')],
        [sg.Text('Автор', size=(20, 1)), sg.InputText(key='-AUTHOR-')],
        [sg.Button('Придбати'), sg.Button('Відміна')]
    ]
    window = sg.Window('Придбання матеріалів', layout)


    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Придбати':
            try:
                title = values['-TITLE-']
                author = values['-AUTHOR-']
                buy_material(title, author)
                break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def buy_material(title, author):
    login = user_db_config['user']
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT client_id FROM client WHERE login = %s"
        cursor.execute(select_query, (login,))
        result = cursor.fetchone()
        
        if result is None:
            sg.popup('Помилка: не знайдено клієнта з таким логіном')
            return

        client_id = result[0]

        buy_query = "UPDATE client SET purchases = purchases + 1 WHERE client_id= %s"
        cursor.execute(buy_query, (client_id,))
        update_query = """
        UPDATE client
        SET status = CASE
            WHEN purchases >= 10 THEN 'regular'
            WHEN purchases >= 100 THEN 'vip'
            ELSE status
        END
        WHERE client_id= %s;
        """
        cursor.execute(update_query, (client_id,))
        connection.commit()
        if cursor.rowcount == 0:
            sg.popup('Помилка: Запит не знайдено або ви не маєте права його видаляти')
        else:
            sg.popup('Матеріал успішно придбано')
    except Exception as e:
        sg.popup(f"Помилка придбання матеріалу: {e}")
    finally:
        cursor.close()
        connection.close()

def get_published_materials():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = """
        SELECT I.title, I.author, I.genre, I.form, I.age_restriction, circulation, publishing_date FROM published_material
        P INNER JOIN material_info I ON I.material_id=P.material_id
        """
        cursor.execute(select_query)
        materials = cursor.fetchall()
        return materials
    except Exception as e:
        sg.popup(f"Помилка при отриманні опублікованих матеріалів: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def create_new_request(title, author, comment):
    login = user_db_config['user']
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT client_id FROM client WHERE login = %s"
        cursor.execute(select_query, (login,))
        result = cursor.fetchone()
        
        if result is None:
            sg.popup('Помилка: не знайдено клієнта з таким логіном')
            return

        client_id = result[0]

        insert_query = """
        INSERT INTO request (client_id, title, author, status, request_date, comment) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (client_id, title, author, 'processing', date.today(), comment))
        connection.commit()
        sg.popup('Новий запит успішно створено')
    except Exception as e:
        sg.popup(f"Помилка при створенні нового запиту: {e}")
    finally:
        cursor.close()
        connection.close()

def view_requests_window():
    requests = get_requests()
    
    layout = [
        [sg.Text('Актуальні запити')],
        [sg.Listbox(values=[f"Назва: {request[2]}, Автор: {request[3]}, Статус: {request[4]}, Коментар: {request[5]}" for request in requests], size=(100, 20), key='-REQUEST_LIST-')],
        [sg.Button('Створити новий запит'), sg.Button('Видалити запит'), sg.Button('Назад')]
    ]
    window = sg.Window('Актуальні запити', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Назад':
            break

        if event == 'Створити новий запит':
            create_new_request_window()
        if event == 'Видалити запит':
            delete_request_window()

    window.close()

def create_new_request_window():
    layout = [
        [sg.Text('Назва', size=(20, 1)), sg.InputText(key='-TITLE-')],
        [sg.Text('Автор', size=(20, 1)), sg.InputText(key='-AUTHOR-')],
        [sg.Text('Коментар', size=(20, 1)), sg.Multiline(key='-COMMENT-')],
        [sg.Button('Створити запит'), sg.Button('Відміна')]
    ]
    window = sg.Window('Створення нового запиту', layout)


    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Створити запит':
            try:
                # client_id = int(values['-CLIENT_ID-'])
                title = values['-TITLE-']
                author = values['-AUTHOR-']
                comment = values['-COMMENT-']
                create_new_request(title, author, comment)
                break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def delete_request(title, author):
    login = user_db_config['user']
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT client_id FROM client WHERE login = %s"
        cursor.execute(select_query, (login,))
        result = cursor.fetchone()
        
        if result is None:
            sg.popup('Помилка: не знайдено клієнта з таким логіном')
            return

        client_id = result[0]

        delete_query = "DELETE FROM request WHERE title = %s AND author = %s AND client_id = %s"
        cursor.execute(delete_query, (title, author, client_id))
        connection.commit()
        if cursor.rowcount == 0:
            sg.popup('Помилка: Запит не знайдено або ви не маєте права його видаляти')
        else:
            sg.popup('Запит успішно видалено')
    except Exception as e:
        sg.popup(f"Помилка при видаленні запиту: {e}")
    finally:
        cursor.close()
        connection.close()

def delete_request_window():
    layout = [
        [sg.Text('Назва', size=(20, 1)), sg.InputText(key='-TITLE-')],
        [sg.Text('Автор', size=(20, 1)), sg.InputText(key='-AUTHOR-')],
        [sg.Button('Видалити запит'), sg.Button('Відміна')]
    ]
    window = sg.Window('Видалення запиту', layout)


    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Відміна':
            break

        if event == 'Видалити запит':
            try:
                title = values['-TITLE-']
                author = values['-AUTHOR-']
                delete_request(title, author)
                break
            except ValueError as ve:
                sg.popup(f"Помилка введення даних: {ve}")

    window.close()

def get_to_print_contracts():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        select_query = "SELECT * FROM contract WHERE status = 'to print'"
        cursor.execute(select_query)
        contracts = cursor.fetchall()
        return contracts
    except Exception as e:
        sg.popup(f"Помилка при отриманні контрактів: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

def publicate_material(contract_id):
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        
        # Перевірка, чи існує контракт зі статусом "to print"
        select_query = "SELECT * FROM contract WHERE contract_id = %s AND status = 'to print'"
        cursor.execute(select_query, (contract_id,))
        contract = cursor.fetchone()
        
        if contract is None:
            sg.popup('Контракт з таким ID не знайдено або його статус не "to print"')
            return
        
        # Додавання запису в таблицю published_material
        insert_query = """
        INSERT INTO published_material (material_id, circulation, publishing_date, responsible_worker)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (contract[2], contract[3], date.today(), contract[1]))
        
        # Оновлення статусу контракту
        update_query = "UPDATE contract SET status = 'printed' WHERE contract_id = %s"
        cursor.execute(update_query, (contract_id,))
        
        connection.commit()
        sg.popup('Матеріал успішно опубліковано')
    except Exception as e:
        sg.popup(f"Помилка при публікації матеріалу: {e}")
    finally:
        cursor.close()
        connection.close()

def publicate_material_window():
    contracts = get_contracts()
    
    layout = [
        [sg.Text('Оберіть контракт для публікації')],
        [sg.InputText(key='-CONTRACT_ID-', size=(20, 1))],
        [sg.Table(values=[list(row) for row in contracts],
                  headings=['ID', 'Працівник', 'Матеріал', 'Тираж', 'Статус', 'Дата зміни', 'Попередній статус'],
                  auto_size_columns=True, key='-CONTRACT_LIST-', enable_events=True)],
        [sg.Button('Опублікувати матеріал'), sg.Button('Відміна')]
    ]
    window = sg.Window('Опублікування матеріалу', layout)

    while True:
        event, values = window.read()
        
        if event in (sg.WINDOW_CLOSED, 'Відміна'):
            break
        
        if event == 'Опублікувати матеріал':
            contract_id = values['-CONTRACT_ID-'] or (values['-CONTRACT_LIST-'][0][0] if values['-CONTRACT_LIST-'] else None)
            if contract_id:
                publicate_material(contract_id)
                window['-CONTRACT_LIST-'].update(values=[list(row) for row in get_contracts()])
    
    window.close()

# def publicate_material_window():
    # contracts = get_contracts()
    
    # layout = [
        # [sg.Text('Введіть ID контракту для публікації'), sg.InputText(key='-CONTRACT_ID-')],
        # [sg.Button('Опублікувати матеріал'), sg.Button('Відміна')],
        # [sg.Text('Контракти')],
        # [sg.Listbox(values=[
            # f"ID: {contract[0]}, Працівник: {contract[1]}, Матеріал: {contract[2]}, Тираж: {contract[3]}, Статус: {contract[4]}, Дата зміни: {contract[5]}, Попередній статус: {contract[6]}"
            # for contract in contracts], size=(100, 20), key='-CONTRACT_LIST-')]
    # ]
    # window = sg.Window('Опублікування матеріалу', layout)

    # while True:
        # event, values = window.read()
        
        # if event == sg.WINDOW_CLOSED or event == 'Відміна':
            # break
        
        # if event == 'Опублікувати матеріал':
            # contract_id = values['-CONTRACT_ID-']
            # try:
                # contract_id = int(contract_id)
                # publicate_material(contract_id)
                # contracts = get_contracts()  # Оновлюємо список контрактів після публікації
                # window['-CONTRACT_LIST-'].update(values=[
                    # f"ID: {contract[0]}, Працівник: {contract[1]}, Матеріал: {contract[2]}, Тираж: {contract[3]}, Статус: {contract[4]}, Дата зміни: {contract[5]}, Попередній статус: {contract[6]}"
                    # for contract in contracts
                # ])
            # except ValueError:
                # sg.popup('Помилка: ID контракту має бути числом')
            # except Exception as e:
                # sg.popup(f"Помилка при публікації матеріалу: {e}")

    # window.close()

### Director Window ######

# Функція для створення окремого вікна з графіком
def create_graph_window(title, x_label, y_label, data, colors):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(data[0], data[1], color=colors)
    ax.set_xlabel(x_label)
    ax.set_title(title)

    layout = [
        [sg.Canvas(key='-CANVAS-')],
    ]

    window = sg.Window(title, layout, finalize=True, element_justification='center', resizable=True)

    # Додавання графіка до вікна
    canvas = FigureCanvasTkAgg(fig, master=window['-CANVAS-'].TKCanvas)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

    return window, fig

# Функція для відображення аналітичних даних
def show_analytics_data():
    results = execute_sql_queries()

    # Створення графіків
    graph_windows = []

    # Графік для найпопулярніших матеріалів (query1)
    titles1 = [row[0] for row in results['query1']]
    request_quantities = [row[2] for row in results['query1']]
    colors1 = plt.cm.viridis(range(len(titles1)))
    window1, fig1 = create_graph_window(
        'Найпопулярніші матеріали за кількістю замовлень',
        'Request Quantity',
        'Матеріали',
        (titles1, request_quantities),
        colors1
    )
    graph_windows.append((window1, fig1))

    # Графік для працівників з найбільшою кількістю публікацій (query2)
    workers = [row[0] for row in results['query2']]
    publications = [row[1] for row in results['query2']]
    colors2 = plt.cm.plasma(range(len(workers)))
    window2, fig2 = create_graph_window(
        'Працівники з найбільшою кількістю публікацій',
        'Publications',
        'Працівники',
        (workers, publications),
        colors2
    )
    graph_windows.append((window2, fig2))

    # Графік для матеріалів з найбільшими тиражами (query3)
    titles3 = [row[0] for row in results['query3']]
    circulations = [row[2] for row in results['query3']]
    colors3 = plt.cm.inferno(range(len(titles3)))
    window3, fig3 = create_graph_window(
        'Матеріали з найбільшими тиражами',
        'Circulation',
        'Матеріали',
        (titles3, circulations),
        colors3
    )
    graph_windows.append((window3, fig3))

    # Головне вікно для керування графіками
    layout = [
        [sg.Text('Аналітичні дані відображені в окремих вікнах.')],
        [sg.Button('Вихід')]
    ]

    main_window = sg.Window('Аналітичні дані', layout, finalize=True)

    while True:
        event, values = main_window.read()
        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break

    # Закриття всіх графіків при закритті головного вікна
    for window, fig in graph_windows:
        window.close()
        plt.close(fig)

    main_window.close()

# def show_analytics_data():
    # results = execute_sql_queries()

    # layout = [
        # [sg.Text('Результати SQL-запитів:')],
        # [sg.Text('1. Найпопулярніші матеріали за кількістю замовлень')],
        # [sg.Table(values=[list(row) for row in results['query1']], headings=['Title', 'Author', 'Request quantity'], auto_size_columns=True)],
        # [sg.Text('2. Відповідальні працівники за найбільшу кількість опублікованих матеріалів:')],
        # [sg.Table(values=[list(row) for row in results['query2']], headings=['Worker', 'Publications'], auto_size_columns=True)],
        # [sg.Text('3. Матеріали з найбільшими та найменшими тиражами за цей рік:')],
        # [sg.Table(values=[list(row) for row in results['query3']], headings=['Title', 'Author', 'Circulation'], auto_size_columns=True)],
        # [sg.Button('Назад')]
    # ]

    # window = sg.Window('Аналітичні дані', layout)

    # while True:
        # event, values = window.read()

        # if event == sg.WINDOW_CLOSED or event == 'Назад':
            # break

    # window.close()

def get_active_contracts():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT contract_id, worker_login, material_title FROM active_contracts")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
    except Exception as e:
        sg.popup(f"Помилка при отриманні даних: {e}")
        return

    layout = [
        [sg.Text('Активні контракти')],
        [sg.Table(values=[list(row) for row in results], headings=['Contract ID', 'Worker', 'Title'], auto_size_columns=True)],
        [sg.Button('Назад')]
    ]

    window = sg.Window('Активні контракти', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Назад':
            break

    window.close()

def execute_sql_queries():
    results = {}
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()

        # Запит 1 найпопуляніші матеріали за кількістю замовлень
        query1 = """
        SELECT M.title, M.author, COUNT(R.title) AS req_count
        FROM material_info M
        INNER JOIN request R ON M.title = R.title
        GROUP BY M.title, M.author
        ORDER BY req_count DESC
        LIMIT 10;
        """
        cursor.execute(query1)
        results['query1'] = cursor.fetchall()

        # Запит 2 Відповідальні працівники за найбільшу кількість опублікованих матеріалів
        query2 = """
        SELECT W.login, COUNT(P.material_id) AS pub_count
        FROM worker W
        INNER JOIN published_material P ON W.worker_id = P.responsible_worker
        GROUP BY W.login
        ORDER BY pub_count DESC
        LIMIT 10; 
        """
        cursor.execute(query2)
        results['query2'] = cursor.fetchall()

        # Запит 3 Матеріали з найбільшими  тиражами за певний період
        query3 = """
        SELECT M.title, M.author, P.circulation
        FROM material_info M
        INNER JOIN published_material P ON M.material_id = P.material_id
        WHERE P.publishing_date BETWEEN '2024-01-01' AND '2024-12-31'
        ORDER BY P.circulation DESC
        LIMIT 10;

        """
        cursor.execute(query3)
        results['query3'] = cursor.fetchall()

    except Exception as e:
        sg.popup(f"Помилка при виконанні запитів: {e}")
    finally:
        cursor.close()
        connection.close()

    return results

# Функція для виклику процедури 3: Щомісячний звіт про публікації
def show_monthly_publication_report():
    try:
        connection = psycopg.connect(**user_db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM monthly_publication_report()")
        results = cursor.fetchall()
    except Exception as e:
        sg.popup(f"Помилка при отриманні щомісячного звіту: {e}")
        results = []
    finally:
        cursor.close()
        connection.close()

    layout = [
        [sg.Text('Щомісячний звіт про публікації:')],
        [sg.Table(values=[list(row) for row in results], headings=['Title', 'Author', 'Circulation', 'Publishing date'], auto_size_columns=True)],
        [sg.Button('Назад')]
    ]

    window = sg.Window('Щомісячний звіт', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Назад':
            break

    window.close()

def show_lastest_publications():
    results = get_latest_publications()
    layout = [
        [sg.Text('Останні публікації')],
        [sg.Table(values=[list(row) for row in results], headings=['Material ID', 'Title', 'Author', 'Circulation', 'Publishing Date'], auto_size_columns=True)],
        [sg.Button('Назад')]
    ]

    window = sg.Window('Останні публікації', layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Назад':
            break

    window.close()

def get_latest_publications():
    connection = psycopg.connect(**user_db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM get_latest_publications();")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def director_window():
    layout = [
        [sg.Button('Переглянути аналітичні дані')],
        [sg.Button('Щомісячний звіт про публікації')],
        [sg.Button('Переглянути активні контракти')],
        [sg.Button('Вихід')]
    ]
    window = sg.Window('Інтерфейс директора', layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break

        if event == 'Переглянути аналітичні дані':
            show_analytics_data()

        if event == 'Щомісячний звіт про публікації':
            show_monthly_publication_report()

        if event == 'Переглянути останні 10 публікацій':
            show_lastest_publications()

        if event == 'Переглянути активні контракти':
            get_active_contracts()

    window.close()


def main():
    login_window = create_login_window()

    while True:
        event, values = login_window.read()
        if event == sg.WINDOW_CLOSED or event == 'Вихід':
            break
        if event == 'Увійти':
            username = values['-USERNAME-']
            password = values['-PASSWORD-']
            if authenticate_user(username, password):
                user_role = get_user_role(username, password)
                login_window.close()
                main_window = create_main_window(user_role)
                while True:
                    main_event, main_values = main_window.read()
                    if main_event == sg.WINDOW_CLOSED or main_event == 'Вихід':
                        break
                    elif main_event == 'Вікно адміністратора':
                        main_window.hide()
                        admin_main()
                        main_window.un_hide()
                    elif main_event == 'Вікно редактора':
                        main_window.hide()
                        editor_main()
                        main_window.un_hide()
                    elif main_event == 'Вікно директора':
                        main_window.hide()
                        director_window()
                        main_window.un_hide()
                    elif main_event == 'Вікно клієнта':
                        main_window.hide()
                        client_interface_window()
                        main_window.un_hide()
            else:
                continue
        if event == 'Реєстрація':
            login_window.hide()
            registration_window = create_registration_window()
            while True:
                reg_event, reg_values = registration_window.read()
                if reg_event == sg.WINDOW_CLOSED or reg_event == 'Назад':
                    registration_window.close()
                    login_window.un_hide()
                    break
                if reg_event == 'Зареєструватися':
                    reg_username = reg_values['-REG_USERNAME-']
                    reg_password = reg_values['-REG_PASSWORD-']
                    reg_password = reg_values['-REG_PASSWORD-']
                    reg_firstname= reg_values['-REG_FIRSTNAME-']
                    reg_lastname = reg_values['-REG_LASTNAME-']
                    reg_phonenumber = reg_values['-REG_PHONENUMBER-']
                    reg_birthday = reg_values['-REG_BIRTHDAY-']
                    if create_client(reg_username, reg_password, reg_firstname, reg_lastname, reg_phonenumber, reg_birthday):
                        registration_window.close()
                        login_window.un_hide()
                        break
    login_window.close()

if __name__ == '__main__':
    main()
