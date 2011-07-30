# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'GameSession.state'
        db.alter_column('game_gamesession', 'state', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'GameSession.client_state'
        db.alter_column('game_gamesession', 'client_state', self.gf('django.db.models.fields.CharField')(max_length=50))


    def backwards(self, orm):
        
        # Changing field 'GameSession.state'
        db.alter_column('game_gamesession', 'state', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'GameSession.client_state'
        db.alter_column('game_gamesession', 'client_state', self.gf('django.db.models.fields.IntegerField')())


    models = {
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'desk_cards': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "''", 'max_length': '250'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'remaining_cards': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '250'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'game.gamesession': {
            'Meta': {'object_name': 'GameSession'},
            'client_state': ('django.db.models.fields.CharField', [], {'default': "'ACTIVE'", 'max_length': '50'}),
            'failures': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_access': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'set_pressed_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sets_found': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'IDLE'", 'max_length': '50'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['game']
