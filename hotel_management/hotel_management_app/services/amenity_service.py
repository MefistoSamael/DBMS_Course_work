from django.db import connection


class AmenityService:
    @staticmethod
    def get_amenities_names_and_ids():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name
                FROM hotel_management_app_amenity
                WHERE deleted_at IS NULL
                ORDER BY name ASC;
            """
            )
            result = cursor.fetchall()

        if result:
            return result
        return []

    @staticmethod
    def get_all_amenities_by_room_id(room_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT a.name, a.description
                FROM hotel_management_app_amenity a
                JOIN hotel_management_app_roomamenity ra ON a.id = ra.amenity_id
                WHERE ra.room_id = %s and a.deleted_at IS NULL and ra.deleted_at IS NULL;
            """,
                [room_id],
            )
            return cursor.fetchall()
