from django.db import connection


class HotelFacilityService:
    @staticmethod
    def get_hotel_facilities(hotel_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description, is_available
                FROM hotel_management_app_hotelfacility
                WHERE hotel_id = %s AND deleted_at IS NULL
                ORDER BY is_available DESC, name ASC
            """,
                [hotel_id],
            )
            return cursor.fetchall()
