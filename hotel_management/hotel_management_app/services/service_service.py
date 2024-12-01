from django.db import connection


class ServiceService:
    @staticmethod
    def get_services_by_hotel_id(hotel_id=1):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description, price
                FROM hotel_management_app_service
                WHERE hotel_id = %s AND deleted_at IS NULL
                ORDER BY id
            """,
                [hotel_id],
            )
            return cursor.fetchall()
