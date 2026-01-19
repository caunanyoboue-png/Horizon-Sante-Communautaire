from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0002_cassuivi"),
    ]

    operations = [
        migrations.AddField(
            model_name="patient",
            name="date_dernier_acces",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

