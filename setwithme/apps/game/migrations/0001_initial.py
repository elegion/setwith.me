# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Game'
        db.create_table('game_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True)),
            ('cards', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=250)),
        ))
        db.send_create_signal('game', ['Game'])

        # Adding model 'GameSession'
        db.create_table('game_gamesession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['game.Game'], null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sets_found', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('failures', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('game', ['GameSession'])


    def backwards(self, orm):
        
        # Deleting model 'Game'
        db.delete_table('game_game')

        # Deleting model 'GameSession'
        db.delete_table('game_gamesession')


    models = {
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'cards': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '250'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'game.gamesession': {
            'Meta': {'object_name': 'GameSession'},
            'failures': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sets_found': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['game']
