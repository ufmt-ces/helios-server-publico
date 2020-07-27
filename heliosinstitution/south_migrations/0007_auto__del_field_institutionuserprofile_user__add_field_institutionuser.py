# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'InstitutionUserProfile.user'
        db.delete_column(u'heliosinstitution_institutionuserprofile', 'user_id')

        # Adding field 'InstitutionUserProfile.helios_user'
        db.add_column(u'heliosinstitution_institutionuserprofile', 'helios_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['helios_auth.User'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'InstitutionUserProfile.user'
        db.add_column(u'heliosinstitution_institutionuserprofile', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['helios_auth.User'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'InstitutionUserProfile.helios_user'
        db.delete_column(u'heliosinstitution_institutionuserprofile', 'helios_user_id')


    models = {
        u'helios_auth.user': {
            'Meta': {'unique_together': "(('user_type', 'user_id'),)", 'object_name': 'User'},
            'admin_p': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('helios_auth.jsonfield.JSONField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'token': ('helios_auth.jsonfield.JSONField', [], {'null': 'True'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'heliosinstitution.institution': {
            'Meta': {'object_name': 'Institution'},
            'address': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idp_address': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'main_phone': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'mngt_email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'sec_phone': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'heliosinstitution.institutionuserprofile': {
            'Meta': {'object_name': 'InstitutionUserProfile'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'helios_user': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['helios_auth.User']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['heliosinstitution.Institution']"})
        }
    }

    complete_apps = ['heliosinstitution']