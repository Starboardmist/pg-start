import re
import subprocess
import psycopg2
import socket


# Функция проверки IP адресов на верность ввода
def is_valid_ip(ip):
    # Проверка базового формата IPv4
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if not pattern.match(ip):
        return False
    # Проверка диапазона каждого октета
    return all(0 <= int(part) <= 255 for part in ip.split("."))
# Функция ввода IP адресов
def get_valid_ips():
    while True:
        ip_input = input("Введите два IP-адреса через запятую: ")
        ip_list = [ip.strip() for ip in ip_input.split(',') if ip.strip()]
        ssh_way = input("Введите путь до приватного ssh ключа: ~/")
        # Функция проверка того, что введено 2 IP адреса
        if len(ip_list) != 2:
            print("Нужно ввести ровно два IP-адреса, разделённых запятой.")
            continue
        # Присваивание переменных
        ip1, ip2 = ip_list

        if not is_valid_ip(ip1) or not is_valid_ip(ip2):
            print("Один или оба IP-адреса некорректны. Попробуйте снова.")
            continue

        return ip1, ip2, ssh_way
# Создание и запись файла inventory.ini
def create_inventory(ip1, ip2, ssh_way):
    inventory_content = f"""[servers]
server1 ansible_host={ip1} ansible_user=ansible ansible_ssh_privat_key_file={ssh_way}
server2 ansible_host={ip2} ansible_user=ansible ansible_ssh_privat_key_file={ssh_way}
"""
    with open("inventory.ini", "w") as f:
        f.write(inventory_content)

    print("Файл inventory.ini успешно создан!")
    print(inventory_content)
# Функция запуска playbook Ansible
def run_playbook():
    print("Запуск playbook.yaml...")
    try:
        subprocess.run(["ansible-playbook", "playbook_that_was_yes.yaml", "-i", "inventory.ini"], check=True)
        print("Playbook выполнен успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении playbook:")
        print(e)
        return False

def check_postgres_via_psql(port=5432, user="timur", dbname="my_database"):
    
    for ip in ip1, ip2:
        try:
            print(f"Проверка PostgreSQL на {ip}:{port}")
            result = subprocess.run(
                ["psql", "-h", ip, "-p", str(port), "-U", user, "-d", dbname, "-c", "SELECT 1;"],
                check=True,
                capture_output=True,
                text=True,
                env={"PGPASSWORD": "12345"}  # Тут вставляем пароль
            )
            return ip
        except subprocess.CalledProcessError as e:
            print("Нет подходящего подключения")
            return False

# Функция выполнения SQL запроса SELECT 1
def execute_select_one(ip):
    try:
        # Подключение к базе данных PostgreSQL
        connection = psycopg2.connect(
            host=ip,
            database="my_database",
            user="timur",
            password="12345"
        )

        # Создаем курсор для выполнения операций с базой данных
        cursor = connection.cursor()

        # Выполняем SQL-запрос
        cursor.execute("SELECT 1;")

        # Получаем результат
        result = cursor.fetchone()
        print("Результат запроса:", result[0])

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        # Закрытие подключения
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто")

if __name__ == "__main__":
    ip1, ip2, ssh_way = get_valid_ips()
    create_inventory(ip1, ip2, ssh_way)
    if run_playbook():
        execute_select_one(check_postgres_via_psql())