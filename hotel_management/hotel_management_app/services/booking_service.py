from django.db import connection, transaction


class BookingService:
    @staticmethod
    def create_booking(guest_id, room_id, check_in_date, check_out_date):
        with connection.cursor() as cursor, transaction.atomic():
            cursor.execute(
                """
                SELECT check_in_date, check_out_date FROM hotel_management_app_booking
                WHERE room_id = %s
                  AND (
                      (check_in_date <= %s AND check_out_date >= %s) OR
                      (check_in_date <= %s AND check_out_date >= %s)
                  )
            """,
                [room_id, check_out_date, check_in_date, check_in_date, check_out_date],
            )

            existing_booking = cursor.fetchone()

            if existing_booking:
                existing_check_in, existing_check_out = existing_booking
                overlap_start = max(existing_check_in, check_in_date)
                overlap_end = min(existing_check_out, check_out_date)
                raise Exception(
                    f"Booking already exists from {overlap_start} to {overlap_end}"
                )

            total_price = BookingService.calculate_total_price(
                check_in_date, check_out_date, room_id, cursor
            )

            cursor.execute(
                """
                INSERT INTO hotel_management_app_booking (guest_id, room_id, check_in_date, check_out_date, total_price, is_paid, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """,
                [guest_id, room_id, check_in_date, check_out_date, total_price, False],
            )
            booking_id = cursor.fetchone()[0]

        return booking_id

    @staticmethod
    def calculate_total_price(check_in_date, check_out_date, room_id, cursor):
        cursor.execute(
            """
            SELECT price_per_night FROM hotel_management_app_room WHERE id = %s AND deleted_at is NULL
        """,
            [room_id],
        )
        room_price_row = cursor.fetchone()

        if not room_price_row:
            raise ValueError("Room not found")

        price_per_night = room_price_row[0]
        num_nights = (check_out_date - check_in_date).days + 1

        if num_nights <= 0:
            raise ValueError("Check-out date must be after check-in date")

        total_price = price_per_night * num_nights

        return total_price

    @staticmethod
    def get_user_bookings(user_id):
        with connection.cursor() as cursor, transaction.atomic():
            cursor.execute(
                """
                SELECT b.id, r.number, b.check_in_date, b.check_out_date, b.total_price, b.is_paid, b.room_id
                FROM hotel_management_app_booking b
                LEFT JOIN hotel_management_app_room r ON r.id = b.room_id AND r.deleted_at is NULL
                WHERE b.guest_id = %s AND b.deleted_at IS NULL
                ORDER BY b.check_in_date
            """,
                [user_id],
            )
            return cursor.fetchall()

    @staticmethod
    def cancel_booking(booking_id):
        with connection.cursor() as cursor, transaction.atomic():
            cursor.execute(
                """
                DELETE FROM hotel_management_app_booking 
                WHERE id = %s
            """,
                [booking_id],
            )

    @staticmethod
    def get_total_price(booking_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT total_price FROM hotel_management_app_booking WHERE id = %s",
                [booking_id],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def get_total_price_by_invoice_id(invoice_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT b.total_price 
                FROM hotel_management_app_invoice i 
                LEFT JOIN hotel_management_app_booking b
                ON b.id = i.booking_id AND b.deleted_at IS NULL
                WHERE i.id = %s AND i.deleted_at IS NULL
                """,
                [invoice_id],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def update_is_paid(booking_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE hotel_management_app_booking SET is_paid = TRUE WHERE id = %s",
                [booking_id],
            )
