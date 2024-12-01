from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction


class UserService:
    @staticmethod
    def save_user_phone_number(user: User, phone_number: str) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE accounts_profile SET phone_number = %s WHERE user_id = %s",
                [phone_number, user.id],
            )

    @staticmethod
    def create_user_with_sql(form_data):
        username = form_data["username"]
        first_name = form_data["first_name"]
        last_name = form_data["last_name"]
        email = form_data["email"]
        password = make_password(form_data["password1"])
        phone_number = form_data["phone_number"]

        with transaction.atomic():
            try:
                sql = """
                    INSERT INTO auth_user (username, first_name, last_name, email, password, is_active, is_staff, is_superuser, date_joined)
                    VALUES (%s, %s, %s, %s, %s, TRUE, FALSE, FALSE, NOW())
                    RETURNING id;
                    """

                with connection.cursor() as cursor:
                    cursor.execute(
                        sql, [username, first_name, last_name, email, password]
                    )
                    user_id = cursor.fetchone()[0]

                update_phone_sql = """
                    UPDATE accounts_profile SET phone_number = %s WHERE user_id = %s;
                    """

                with connection.cursor() as cursor:
                    cursor.execute(update_phone_sql, [phone_number, user_id])

                return User(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                )
            except Exception as e:
                raise Exception(f"An error occurred while creating the user: {str(e)}")

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, first_name, last_name, email FROM auth_user WHERE username = %s",
                [username],
            )
            result = cursor.fetchone()

        if result:
            user = User(
                id=result[0],
                username=result[1],
                first_name=result[2],
                last_name=result[3],
                email=result[4],
            )
            return user
        else:
            raise ObjectDoesNotExist(f"User with username '{username}' does not exist.")

    @staticmethod
    def is_user_is_guest(user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT role FROM accounts_profile WHERE user_id = %s
            """,
                [user_id],
            )
            row = cursor.fetchone()
        return row and row[0] == "guest"
