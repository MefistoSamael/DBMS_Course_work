from django.db import connection


class ProfileService:
    @staticmethod
    def get_profile(user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.username, u.email, u.first_name, u.last_name, p.phone_number, p.role
                FROM auth_user u
                JOIN accounts_profile p ON u.id = p.user_id
                WHERE u.id = %s
            """,
                [user_id],
            )
            profile_data = cursor.fetchone()

        return {
            "username": profile_data[0],
            "email": profile_data[1],
            "first_name": profile_data[2],
            "last_name": profile_data[3],
            "phone_number": profile_data[4],
            "role": profile_data[5],
        }

    @staticmethod
    def update_profile(user_id, first_name, last_name, phone_number):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE auth_user
                SET first_name = %s, last_name = %s
                WHERE id = %s
            """,
                [first_name, last_name, user_id],
            )

            cursor.execute(
                """
                UPDATE accounts_profile
                SET phone_number = %s
                WHERE user_id = %s
            """,
                [phone_number, user_id],
            )
