# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projeng', '0011_remove_layer_geometry'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['status'], name='projeng_pro_status_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['barangay'], name='projeng_pro_barangay_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['created_at'], name='projeng_pro_created_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['updated_at'], name='projeng_pro_updated_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['start_date', 'end_date'], name='projeng_pro_dates_idx'),
        ),
        migrations.AddIndex(
            model_name='projectprogress',
            index=models.Index(fields=['project', '-date'], name='projeng_proj_proj_date_idx'),
        ),
        migrations.AddIndex(
            model_name='projectcost',
            index=models.Index(fields=['project', 'date'], name='projeng_proj_proj_cost_date_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', '-created_at'], name='projeng_notif_recip_created_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='projeng_notif_recip_read_idx'),
        ),
    ]

