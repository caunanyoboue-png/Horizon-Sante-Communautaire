from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0003_patient_date_dernier_acces"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="patient",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

