# Generated by Django 3.1.1 on 2020-10-12 09:59

from django.db import migrations, models


def create_initial_tags(apps, schema_editor):
    """
    Initializing some initial tags, which would be the same in dev and prod envs.

    Those initial tags are:
    - Others
    - Animals
    - Anime
    - Consoles
    - Drugs
    - Politics
    """
    Tag = apps.get_model('srachat', 'Tag')
    for tag_name in ["Others", "Animals", "Anime", "Consoles", "Drugs", "Politics"]:
        Tag.objects.create(name=tag_name)


class Migration(migrations.Migration):

    dependencies = [
        ('srachat', '0007_merge_20200406_0200'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='room',
            name='tags',
            field=models.ManyToManyField(related_name='rooms', to='srachat.Tag'),
        ),
        migrations.RunPython(create_initial_tags)
    ]
