# Generated by Django 2.2.13 on 2020-07-13 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qdjango', '0049_layer_download_gpx'),
        ('eleprofile', '0003_auto_20200709_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='eleprodtm',
            name='layers',
            field=models.ManyToManyField(related_name='path_layer', to='qdjango.Layer'),
        ),
        migrations.AlterField(
            model_name='eleprodtm',
            name='dtm_layer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dtm_layer', to='qdjango.Layer'),
        ),
        migrations.DeleteModel(
            name='EleProLayer',
        ),
    ]
