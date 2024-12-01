from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("hotel_management_app", "0003_create_user_activity_log_table"),
    ]

    operations = [
        migrations.RunSQL("CREATE INDEX idx_room_hotel_id ON hotel_management_app_room(hotel_id);"),

        migrations.RunSQL("CREATE INDEX idx_roomimage_room_id ON hotel_management_app_roomimage(room_id);"),

        migrations.RunSQL("CREATE INDEX idx_booking_user_id ON hotel_management_app_booking(guest_id);"),
        migrations.RunSQL("CREATE INDEX idx_booking_room_id ON hotel_management_app_booking(room_id);"),

        migrations.RunSQL("CREATE INDEX idx_feedback_room_id ON hotel_management_app_feedback(room_id);"),
        migrations.RunSQL("CREATE INDEX idx_feedback_user_id ON hotel_management_app_feedback(guest_id);"),

        migrations.RunSQL("CREATE INDEX idx_invoice_booking_id ON hotel_management_app_invoice(booking_id);"),

        migrations.RunSQL("CREATE INDEX idx_payment_invoice_id ON hotel_management_app_payment(invoice_id);"),

        migrations.RunSQL("CREATE INDEX idx_service_hotel_id ON hotel_management_app_service(hotel_id);"),

        migrations.RunSQL("CREATE INDEX idx_event_hotel_id ON hotel_management_app_event(hotel_id);"),

        migrations.RunSQL("CREATE INDEX idx_hotel_facility_hotel_id ON hotel_management_app_hotelfacility(hotel_id);"),
    ]
