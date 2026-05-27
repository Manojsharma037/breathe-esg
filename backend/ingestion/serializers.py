from rest_framework import serializers
from records.models import DataUpload, RawRecord, NormalizedRecord, AuditLog

class DataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataUpload
        fields = ['id', 'source_type', 'file_name',
                  'status', 'uploaded_at', 'row_count']

class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = ['id', 'row_number', 'raw_data',
                  'status', 'created_at']

class NormalizedRecordSerializer(serializers.ModelSerializer):
    source_type = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'scope', 'category',
            'quantity', 'original_unit',
            'co2_equivalent', 'period_start', 'period_end',
            'review_status', 'reviewed_by', 'reviewed_at',
            'review_note', 'is_suspicious', 'suspicious_reason',
            'is_locked', 'source_type', 'created_at'
        ]

    def get_source_type(self, obj):
        return obj.raw_record.upload.source_type

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'note', 'timestamp']