from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # Creating the 'profile' table
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS  accounts_profile (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                deleted_at TIMESTAMP WITH TIME ZONE,
                user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE,
                phone_number VARCHAR(11) NOT NULL,
                "role" VARCHAR(10) NOT NULL CHECK (role IN ('guest', 'admin')) DEFAULT 'guest'
            );
            """
        ),
        # Adding the signal-based functionality for auto-creating/updating profiles
        migrations.RunSQL(
            """
CREATE OR REPLACE FUNCTION create_or_update_user_profile()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW IS NULL THEN
        RETURN NULL;
    END IF;

    IF (TG_OP = 'INSERT') THEN
        IF NEW.is_superuser OR NEW.is_staff THEN
            INSERT INTO accounts_profile (user_id, phone_number, role, created_at, updated_at)
            VALUES (NEW.id, '80291234567', 'admin', NOW(), NOW());
        ELSE
            INSERT INTO accounts_profile (user_id, phone_number, role)
            VALUES (NEW.id, '80291234567', 'guest');
        END IF;
    ELSE
        UPDATE accounts_profile SET user_id = NEW.id, updated_at = NOW() WHERE user_id = OLD.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

            -- Trigger to run after user is inserted or updated
            CREATE TRIGGER after_user_insert
            AFTER INSERT OR UPDATE ON auth_user
            FOR EACH ROW
            EXECUTE FUNCTION create_or_update_user_profile();

            """
        ),
    ]
