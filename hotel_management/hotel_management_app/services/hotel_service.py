from django.db import connection

from ..constants import DEFAULT_HOTEL_FACILITIES, DEFAULT_HOTEL_INFO
from ..models import Hotel
from . import AbstractService


class HotelService(AbstractService):
    @staticmethod
    def get_first_hotel_info_with_facilities():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT h.name, h.description, h.location, h.image,
                       JSON_AGG(hf) AS facilities, h.id
                FROM hotel_management_app_hotel AS h
                LEFT JOIN (
                    SELECT hf.name, hf.description, hf.hotel_id
                    FROM hotel_management_app_hotelfacility AS hf
                    WHERE hf.deleted_at IS NULL
                    ORDER BY hf.id ASC
                    LIMIT 3
                ) AS hf ON h.id = hf.hotel_id
                WHERE h.deleted_at IS NULL
                GROUP BY h.id
                ORDER BY h.id ASC
                LIMIT 1;
            """
            )
            result = cursor.fetchone()

        if result:
            facilities = (
                result[4]
                if result[4] and result[4][0] is not None
                else DEFAULT_HOTEL_FACILITIES
            )

            hotel_info = {
                "name": result[0],
                "description": result[1],
                "location": result[2],
                "image": result[3],
                "facilities": facilities,
                "id": result[5],
            }
            return hotel_info
        return None

    @staticmethod
    def get_first_hotel_location():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT location
                FROM hotel_management_app_hotel
                WHERE deleted_at IS NULL
                ORDER BY id ASC
                LIMIT 1;
            """
            )
            result = cursor.fetchone()

        if result and result[0] is not None:
            return result[0]
        return DEFAULT_HOTEL_INFO.get("location", "")

    @staticmethod
    def create(obj: Hotel):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO hotel_management_app_hotel (created_at, updated_at, name, description, location, image, deleted_at) VALUES (NOW(), NOW(), %s, %s, %s, %s, %s)",
                [obj.name, obj.description, obj.location, obj.image, obj.deleted_at],
            )

    @staticmethod
    def update(obj: Hotel):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE hotel_management_app_hotel SET name = %s, description = %s, location = %s, image = %s, updated_at = NOW(), deleted_at = %s WHERE id = %s",
                [
                    obj.name,
                    obj.description,
                    obj.location,
                    obj.image,
                    obj.deleted_at,
                    obj.id,
                ],
            )
