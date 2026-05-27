from django.contrib import admin
from .models import (
    Tenant, UserProfile, DataUpload,
    RawRecord, NormalizedRecord, AuditLog
)

admin.site.register(Tenant)
admin.site.register(UserProfile)
admin.site.register(DataUpload)
admin.site.register(RawRecord)
admin.site.register(NormalizedRecord)
admin.site.register(AuditLog)