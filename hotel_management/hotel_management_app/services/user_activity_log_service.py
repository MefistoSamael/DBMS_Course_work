from django.db import connection


class UserActivityLogService:
    @staticmethod
    def log_action(user_id, action_type, model_name, object_id=None, description=None):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO hotel_management_app_useractivitylog (user_id, action_type, model_name, object_id, created_at, description)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """,
                [user_id, action_type, model_name, object_id, description],
            )
