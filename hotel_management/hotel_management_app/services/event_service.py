from datetime import datetime

from django.db import connection


class EventService:
    @staticmethod
    def get_upcoming_events():
        with connection.cursor() as cursor:
            current_date = datetime.now().date()
            cursor.execute(
                """
                SELECT id, name, description, event_date_from, event_date_to, location
                FROM hotel_management_app_event
                WHERE event_date_from >= %s AND deleted_at IS NULL
                ORDER BY event_date_from ASC
            """,
                [current_date],
            )
            events = cursor.fetchall()

        return events
