from django.db import connection


class FeedbackService:
    @staticmethod
    def get_average_room_rating(room_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(rating) as average_rating
                FROM hotel_management_app_feedback f
                WHERE f.deleted_at IS NULL AND f.room_id = %s
            """,
                [room_id],
            )
            average_rating = cursor.fetchone()[0]
            if average_rating:
                return round(average_rating, 1)
            return None

    @staticmethod
    def get_limit_feedbacks_by_room_id(room_id: int, limit: int):
        with connection.cursor() as cursor:
            cursor.execute(
                """
            SELECT f.updated_at, f.rating, f.comments FROM hotel_management_app_feedback f
            WHERE f.room_id = %s AND f.deleted_at IS NULL
            ORDER BY f.updated_at DESC
            LIMIT %s;
            """,
                [room_id, limit],
            )
            return cursor.fetchall()

    @staticmethod
    def add_feedback(guest_id: int, room_id: int, rating: int, comments: str):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO hotel_management_app_feedback (guest_id, room_id, rating, comments, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """,
                (guest_id, room_id, rating, comments),
            )
            return cursor.fetchone()[0]
