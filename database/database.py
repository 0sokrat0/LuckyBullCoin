from datetime import datetime

import mysql.connector

class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        print("Пытаюсь подключиться к базе данных...")
        self.connection = mysql.connector.connect(**db_config)
        self.cursor = self.connection.cursor(buffered=True)
        print("Подключено к:", db_config['host'])

    def user_exists(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchall()
        return bool(result)

    def add_user(self, user_id, referer_id=None, tg_name=None):
        query = "INSERT INTO users (user_id, referer_id, tg_name, bonus_points, registration_date) VALUES (%s, %s, %s, 0, NOW())"
        self.cursor.execute(query, (user_id, referer_id, tg_name))
        self.connection.commit()

    def update_user_tg_name(self, user_id, tg_name):
        query = "UPDATE users SET tg_name = %s WHERE user_id = %s"
        self.cursor.execute(query, (tg_name, user_id))
        self.connection.commit()

    def get_user_info(self, user_id):
        query = "SELECT * FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchone()

    def count_referals(self, user_id):
        query = "SELECT COUNT(*) FROM users WHERE referer_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def add_bonus(self, user_id, bonus_amount):
        query = "UPDATE users SET bonus_points = bonus_points + %s WHERE user_id = %s"
        self.cursor.execute(query, (bonus_amount, user_id))
        self.connection.commit()

    def get_bonus_points(self, user_id):
        query = "SELECT bonus_points FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        self.connection.commit()

    def has_received_bonus_for_channel(self, user_id, channel_id):
        query = "SELECT bonus_received FROM subscriptions WHERE user_id = %s AND channel_id = %s"
        self.cursor.execute(query, (user_id, channel_id))
        result = self.cursor.fetchone()
        return result[0] if result else False


    def mark_bonus_received_for_channel(self, user_id, channel_id):
        query = "INSERT INTO subscriptions (user_id, channel_id, bonus_received) VALUES (%s, %s, TRUE) ON DUPLICATE KEY UPDATE bonus_received = TRUE"
        self.cursor.execute(query, (user_id, channel_id))
        self.connection.commit()

    def count_users_registered_between(self, start_date, end_date):
        query = "SELECT COUNT(*) FROM users WHERE registration_date BETWEEN %s AND %s"
        self.cursor.execute(query, (start_date, end_date))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def increment_referral_count(self, user_id):
        query = "UPDATE users SET referral_count = referral_count + 1 WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        self.connection.commit()

    def get_referral_count(self, user_id):
        query = "SELECT referral_count FROM users WHERE user_id = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_last_login(self, user_id):
        now = datetime.now()
        query = "UPDATE users SET last_login = %s WHERE user_id = %s"
        self.cursor.execute(query, (now, user_id))
        self.connection.commit()

    def update_last_activity(self, user_id):
        now = datetime.now()
        query = "UPDATE users SET last_activity = %s WHERE user_id = %s"
        self.cursor.execute(query, (now, user_id))
        self.connection.commit()

    def get_detailed_user_statistics(self):
        statistics = {}
        with self.connection.cursor() as cursor:
            # Общее количество пользователей
            cursor.execute("SELECT COUNT(*) FROM users")
            statistics['total_users'] = cursor.fetchone()[0]

            # Активные пользователи за последнюю неделю
            cursor.execute("SELECT COUNT(*) FROM users WHERE last_activity >= NOW() - INTERVAL 7 DAY")
            statistics['active_users'] = cursor.fetchone()[0]

            # Новые пользователи за последнюю неделю
            cursor.execute("SELECT COUNT(*) FROM users WHERE registration_date >= NOW() - INTERVAL 7 DAY")
            statistics['new_users'] = cursor.fetchone()[0]

            # Среднее количество бонусов на пользователя
            cursor.execute("SELECT AVG(bonus_points) FROM users")
            statistics['average_bonus_per_user'] = cursor.fetchone()[0]

            # Всего бонусов
            cursor.execute("SELECT SUM(bonus_points) FROM users")
            statistics['total_bonus'] = cursor.fetchone()[0]

        return statistics

    def close(self):
        self.cursor.close()
        self.connection.close()
