# Generated migration to add test_case_validation_json field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promptevaluation',
            name='test_case_validation_json',
            field=models.JSONField(default=dict),
        ),
    ]
