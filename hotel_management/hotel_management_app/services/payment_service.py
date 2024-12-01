from django.db import connection

from ..models import Payment


class PaymentService:
    @staticmethod
    def get_total_price_for_invoice(invoice_id: int):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(SUM(amount_paid), 0) FROM hotel_management_app_payment WHERE invoice_id = %s AND deleted_at is NULL",
                [invoice_id],
            )
            return cursor.fetchone()[0]

    @staticmethod
    def create_payment(obj: Payment):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO hotel_management_app_payment (invoice_id, amount_paid, payment_method, created_at, updated_at, deleted_at)
                VALUES (%s, %s, %s, NOW(), NOW(), %s)
                """,
                [obj.invoice_id, obj.amount_paid, obj.payment_method, obj.deleted_at],
            )

    @staticmethod
    def update(obj: Payment):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE hotel_management_app_payment SET invoice_id = %s, amount_paid = %s, payment_method = %s, deleted_at = %s, updated_at = NOW() WHERE id = %s",
                [
                    obj.invoice_id,
                    obj.amount_paid,
                    obj.payment_method,
                    obj.deleted_at,
                    obj.id,
                ],
            )
