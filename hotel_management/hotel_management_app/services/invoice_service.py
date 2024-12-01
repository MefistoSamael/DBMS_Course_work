from django.db import connection, transaction


class InvoiceService:

    @staticmethod
    def get_invoice_details(booking_id):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT i.id, i.created_at, i.total_amount, i.is_paid, i.booking_id
                    FROM hotel_management_app_invoice i
                    WHERE i.booking_id = %s AND i.deleted_at is NULL
                    """,
                    [booking_id],
                )
                invoice = cursor.fetchone()

                if not invoice:
                    return {}

                invoice_data = {
                    "invoice_id": invoice[0],
                    "created_at": invoice[1],
                    "total_amount": invoice[2],
                    "is_paid": invoice[3],
                    "booking_id": invoice[4],
                    "payments": [],
                }

                cursor.execute(
                    """
                    SELECT p.created_at, p.amount_paid, p.payment_method
                    FROM hotel_management_app_payment p
                    WHERE p.invoice_id = %s AND p.deleted_at is NULL
                    ORDER BY p.created_at DESC
                """,
                    [invoice_data.get("invoice_id")],
                )

                payments = cursor.fetchall()

                for payment in payments:
                    invoice_data["payments"].append(
                        {"date": payment[0], "amount": payment[1], "method": payment[2]}
                    )

        return invoice_data

    @staticmethod
    def get_total_amount(invoice_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT total_amount FROM hotel_management_app_invoice WHERE id = %s AND deleted_at is NULL",
                [invoice_id],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def update_is_paid(invoice_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE hotel_management_app_invoice SET is_paid = TRUE WHERE id = %s AND deleted_at is NULL",
                [invoice_id],
            )
