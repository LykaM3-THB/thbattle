# Generated by Django 3.0.3 on 2020-05-16 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('player', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unlocked',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item', models.SlugField(help_text='解锁项目', max_length=256, verbose_name='解锁项目')),
                ('unlocked_at', models.DateTimeField(auto_now_add=True, help_text='日期', verbose_name='日期')),
                ('player', models.ForeignKey(help_text='玩家', on_delete=django.db.models.deletion.CASCADE, related_name='unlocks', to='player.Player', verbose_name='玩家')),
            ],
            options={
                'verbose_name': '解锁',
                'verbose_name_plural': '解锁',
                'unique_together': {('player', 'item')},
            },
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('achievement', models.SlugField(help_text='成就', max_length=256, verbose_name='成就')),
                ('achieved_at', models.DateTimeField(auto_now_add=True, help_text='日期', verbose_name='日期')),
                ('player', models.ForeignKey(help_text='玩家', on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='player.Player', verbose_name='玩家')),
            ],
            options={
                'verbose_name': '成就',
                'verbose_name_plural': '成就',
                'unique_together': {('player', 'achievement')},
            },
        ),
    ]
