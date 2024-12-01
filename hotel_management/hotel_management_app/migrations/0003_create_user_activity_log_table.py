from django.db import migrations


def create_user_activity_log_table(apps, schema_editor):
    schema_editor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_management_app_useractivitylog (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES auth_user(id) ON DELETE SET_NULL,
        action_type VARCHAR(50) CHECK (action_type IN ('create', 'update', 'delete', 'view')) NOT NULL,
        model_name VARCHAR(100) NOT NULL,
        object_id INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        description TEXT
    );
    """
    )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_add_profile"),
        ("hotel_management_app", "0002_add_main_models"),
    ]

    operations = [
        migrations.RunPython(create_user_activity_log_table),
    ]
