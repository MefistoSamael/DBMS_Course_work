from django.db import migrations


def create_hotel_schema(apps, schema_editor):
    schema_editor.execute(
        """
        CREATE TABLE IF NOT EXISTS hotel_management_app_hotel (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        "name" VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        image TEXT,
        location VARCHAR(255)
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_room (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        hotel_id INTEGER NOT NULL REFERENCES hotel_management_app_hotel(id) ON DELETE CASCADE,
        number VARCHAR(10) UNIQUE NOT NULL,
        room_type VARCHAR(10) CHECK (room_type IN ('single', 'double', 'suite')) NOT NULL,
        capacity INTEGER CHECK (capacity >= 1 AND capacity <= 10) NOT NULL,
        price_per_night DECIMAL(10, 2) CHECK (price_per_night > 0) NOT NULL,
        is_available BOOLEAN DEFAULT TRUE NOT NULL,
        description TEXT
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_roomimage (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        room_id INTEGER NOT NULL REFERENCES hotel_management_app_room(id) ON DELETE CASCADE,
        image TEXT NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_booking (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        CONSTRAINT check_deleted_at CHECK (deleted_at IS NULL OR deleted_at > created_at),
        guest_id INTEGER NOT NULL REFERENCES accounts_profile(id) ON DELETE CASCADE,
        room_id INTEGER NOT NULL REFERENCES hotel_management_app_room(id) ON DELETE CASCADE,
        check_in_date DATE NOT NULL,
        check_out_date DATE NOT NULL,
        total_price DECIMAL(10, 2) CHECK (total_price > 0) NOT NULL,
        is_paid BOOLEAN DEFAULT FALSE NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_service (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        hotel_id INTEGER NOT NULL REFERENCES hotel_management_app_hotel(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        price DECIMAL(10, 2) CHECK (price >= 0) NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_invoice (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        CONSTRAINT check_deleted_at CHECK (deleted_at IS NULL OR deleted_at > created_at),
        booking_id INTEGER NOT NULL REFERENCES hotel_management_app_booking(id) ON DELETE CASCADE,
        total_amount DECIMAL(10, 2) CHECK (total_amount > 0) NOT NULL,
        is_paid BOOLEAN DEFAULT FALSE NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_payment (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        CONSTRAINT check_deleted_at CHECK (deleted_at IS NULL OR deleted_at > created_at),
        invoice_id INTEGER NOT NULL REFERENCES hotel_management_app_invoice(id) ON DELETE CASCADE,
        amount_paid DECIMAL(10, 2) CHECK (amount_paid > 0) NOT NULL,
        payment_method VARCHAR(20) CHECK (payment_method IN ('cash', 'credit_card', 'bank_transfer')) NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_amenity (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        CONSTRAINT check_deleted_at CHECK (deleted_at IS NULL OR deleted_at > created_at),
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_roomamenity (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        CONSTRAINT check_deleted_at CHECK (deleted_at IS NULL OR deleted_at > created_at),
        room_id INTEGER NOT NULL REFERENCES hotel_management_app_room(id) ON DELETE CASCADE,
        amenity_id INTEGER NOT NULL REFERENCES hotel_management_app_amenity(id) ON DELETE CASCADE
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_feedback (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        guest_id INTEGER NOT NULL REFERENCES accounts_profile(id) ON DELETE CASCADE,
        room_id INTEGER NOT NULL REFERENCES hotel_management_app_room(id) ON DELETE CASCADE,
        rating INTEGER CHECK (rating >= 0 AND rating <= 5) NOT NULL,
        comments TEXT
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_event (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        hotel_id INTEGER NOT NULL REFERENCES hotel_management_app_hotel(id) ON DELETE CASCADE,
        name VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        event_date_from DATE NOT NULL,
        event_date_to DATE NOT NULL,
        location VARCHAR(255) NOT NULL
    );
    """
    )

    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_hotelfacility (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        deleted_at TIMESTAMP WITH TIME ZONE,
        hotel_id INTEGER NOT NULL REFERENCES hotel_management_app_hotel(id) ON DELETE CASCADE,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        is_available BOOLEAN DEFAULT TRUE NOT NULL
    );
    """
    )


class Migration(migrations.Migration):
    dependencies = [
        ("hotel_management_app", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_hotel_schema),
    ]
