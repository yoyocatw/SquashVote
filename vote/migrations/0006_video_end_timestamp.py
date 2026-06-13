# Adds the optional clip end_timestamp. Deliberately scoped to JUST this field —
# it does NOT touch the pre-existing unique_video_id_timestamp constraint drift
# (see HANDOVER "Next steps"); leave that for its own dedicated migration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0005_video_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='end_timestamp',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
