# Generated by Django 4.2.2 on 2023-07-29 04:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0009_delete_comment'),
        ('comments', '0004_remove_comment_author_remove_comment_board_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='board',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='board.board'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
