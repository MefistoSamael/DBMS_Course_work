from django.db import connection

from ..models import RoomImage
from . import AbstractService


class RoomImageService(AbstractService):
    @staticmethod
    def create(obj: RoomImage):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO hotel_management_app_roomimage (created_at, updated_at, room_id, image) VALUES (NOW(), NOW(), %s, %s)",
                [obj.room_id, obj.image],
            )

    @staticmethod
    def update(obj: RoomImage):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE hotel_management_app_roomimage SET room_id = %s, image = %s, updated_at = NOW(), deleted_at = %s WHERE id = %s",
                [obj.room_id, obj.image, obj.deleted_at, obj.id],
            )

    @staticmethod
    def get_all_room_images_by_room_id(room_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT image FROM hotel_management_app_roomimage
                WHERE room_id = %s AND deleted_at is NULL;
            """,
                [room_id],
            )
            images = cursor.fetchall() or []
            return [img[0] for img in images]
