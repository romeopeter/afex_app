# Generated by Django 4.0.6 on 2022-08-28 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_alter_chat_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='file',
            field=models.FileField(help_text='A file you wish to upload', null=True, upload_to=''),
        ),
    ]
