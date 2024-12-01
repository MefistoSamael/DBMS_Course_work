from django.db import connection

from ..utils import get_start_end_date


class RoomService:
    @staticmethod
    def get_filtered_rooms(filters, limit=10, offset=0, hotel_id=1):
        amenities = filters.get("amenities") or None
        sort_by = filters.get("sort_by", "number")
        sort_order = filters.get("sort_order", "asc")
        date_range = filters.get("date_range")
        start_date, end_date = get_start_end_date(date_range)
        amenities_filter = "AND ra2.amenity_id IN %(amenities)s" if amenities else ""

        if sort_order == "desc":
            order = f"{sort_by} DESC"
        else:
            order = f"{sort_by} ASC"

        sql = f"""
                SELECT r.number, r.room_type, r.capacity, r.price_per_night, r.is_available, 
                       COALESCE(MAX(img.image), '') AS room_image,
                       COALESCE(AVG(f.rating), 0) AS avg_rating,
                       COUNT(f.rating) AS has_feedback,
                       STRING_AGG(DISTINCT a.name, ', ') AS amenities,
                       r.id
                FROM hotel_management_app_room AS r
                LEFT JOIN hotel_management_app_roomimage AS img ON img.room_id = r.id AND img.deleted_at IS NULL
                LEFT JOIN hotel_management_app_feedback AS f ON f.room_id = r.id AND f.deleted_at IS NULL
                LEFT JOIN hotel_management_app_roomamenity AS ra ON ra.room_id = r.id AND ra.deleted_at IS NULL
                LEFT JOIN hotel_management_app_amenity AS a ON a.id = ra.amenity_id AND a.deleted_at IS NULL
                WHERE r.deleted_at IS NULL AND r.hotel_id = %(hotel_id)s
                  AND (%(room_type)s IS NULL OR r.room_type = %(room_type)s)
                  AND (%(capacity_min)s IS NULL OR r.capacity >= %(capacity_min)s)
                  AND (%(capacity_max)s IS NULL OR r.capacity <= %(capacity_max)s)
                  AND (%(price_min)s IS NULL OR r.price_per_night >= %(price_min)s)
                  AND (%(price_max)s IS NULL OR r.price_per_night <= %(price_max)s)
                  AND (%(is_available)s IS NULL OR r.is_available = %(is_available)s)
                  AND (%(amenities)s IS NULL OR EXISTS (
                      SELECT 1 FROM hotel_management_app_roomamenity ra2 
                      WHERE ra2.room_id = r.id AND ra2.deleted_at IS NULL {amenities_filter}
                  ))
                  {('AND NOT EXISTS ('
                    'SELECT 1 FROM hotel_management_app_booking b '
                    'WHERE b.room_id = r.id AND b.deleted_at IS NULL '
                    'AND b.check_in_date <= %(end_date)s AND b.check_out_date >= %(start_date)s)') if start_date and end_date else ''}
                GROUP BY r.id
                ORDER BY {order}
                LIMIT %(limit)s OFFSET %(offset)s;
            """

        params = {
            "hotel_id": hotel_id,
            "room_type": filters.get("room_type") or None,
            "capacity_min": filters.get("capacity_min") or None,
            "capacity_max": filters.get("capacity_max") or None,
            "price_min": filters.get("price_min") or None,
            "price_max": filters.get("price_max") or None,
            "is_available": filters.get("is_available") or None,
            "amenities": tuple(amenities) if amenities else None,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
        }

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rooms = cursor.fetchall()

        return rooms

    @staticmethod
    def get_filtered_rooms_count(filters,hotel_id=1):
        amenities = filters.get("amenities", None)
        date_range = filters.get("date_range")
        start_date, end_date = get_start_end_date(date_range)

        amenities_filter = "AND ra2.amenity_id IN %(amenities)s" if amenities else ""

        sql = f"""
                SELECT COUNT(DISTINCT r.id)
                FROM hotel_management_app_room AS r
                LEFT JOIN hotel_management_app_roomamenity AS ra ON ra.room_id = r.id AND ra.deleted_at IS NULL
                WHERE r.deleted_at IS NULL AND r.hotel_id = %(hotel_id)s
                  AND (%(room_type)s IS NULL OR r.room_type = %(room_type)s)
                  AND (%(capacity_min)s IS NULL OR r.capacity >= %(capacity_min)s)
                  AND (%(capacity_max)s IS NULL OR r.capacity <= %(capacity_max)s)
                  AND (%(price_min)s IS NULL OR r.price_per_night >= %(price_min)s)
                  AND (%(price_max)s IS NULL OR r.price_per_night <= %(price_max)s)
                  AND (%(is_available)s IS NULL OR r.is_available = %(is_available)s)
                  AND (%(amenities)s IS NULL OR EXISTS (
                      SELECT 1 FROM hotel_management_app_roomamenity ra2 
                      WHERE ra2.room_id = r.id AND ra2.deleted_at IS NULL {amenities_filter}
                  ))
                  {('AND NOT EXISTS ('
                    'SELECT 1 FROM hotel_management_app_booking b '
                    'WHERE b.room_id = r.id AND b.deleted_at IS NULL '
                    'AND b.check_in_date <= %(end_date)s AND b.check_out_date >= %(start_date)s)') if start_date and end_date else ''}
                """

        params = {
            "hotel_id": hotel_id,
            "room_type": filters.get("room_type") or None,
            "capacity_min": filters.get("capacity_min") or None,
            "capacity_max": filters.get("capacity_max") or None,
            "price_min": filters.get("price_min") or None,
            "price_max": filters.get("price_max") or None,
            "is_available": filters.get("is_available") or None,
            "amenities": tuple(amenities) if amenities else None,
            "start_date": start_date,
            "end_date": end_date,
        }

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            total_rooms = cursor.fetchone()[0]

        return total_rooms

    @staticmethod
    def get_room_details(room_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.id, r.number, r.room_type, r.capacity, r.price_per_night, r.is_available, h.location, r.description
                FROM hotel_management_app_room r
                JOIN hotel_management_app_hotel h ON r.hotel_id = h.id
                WHERE r.id = %s AND r.deleted_at is NULL;
            """,
                [room_id],
            )
            return cursor.fetchone()
