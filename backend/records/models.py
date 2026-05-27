from django.db import models
from django.contrib.auth.models import User


# ─── Model 1: Tenant ───────────────────────────────
class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)  # e.g. "acme-corp"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ─── Model 2: UserProfile ──────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='users'
    )

    def __str__(self):
        return f"{self.user.username} ({self.tenant.name})"


# ─── Model 3: DataUpload ───────────────────────────
class DataUpload(models.Model):

    SOURCE_CHOICES = [
        ('sap', 'SAP Fuel & Procurement'),
        ('utility', 'Utility Electricity'),
        ('travel', 'Corporate Travel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='uploads'
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    file_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.source_type} - {self.file_name}"


# ─── Model 4: RawRecord ────────────────────────────
class RawRecord(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('normalized', 'Normalized'),
        ('failed', 'Failed'),
    ]

    upload = models.ForeignKey(
        DataUpload, on_delete=models.CASCADE, related_name='raw_records'
    )
    row_number = models.IntegerField()         # CSV ki konsi row thi
    raw_data = models.JSONField()              # Exact row as-is store
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.row_number} - {self.upload.source_type}"


# ─── Model 5: NormalizedRecord ─────────────────────
class NormalizedRecord(models.Model):

    SCOPE_CHOICES = [
        ('scope1', 'Scope 1 - Direct Emissions'),
        ('scope2', 'Scope 2 - Electricity'),
        ('scope3', 'Scope 3 - Value Chain'),
    ]

    REVIEW_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspicious', 'Suspicious'),
    ]

    # Source tracking
    raw_record = models.OneToOneField(
        RawRecord, on_delete=models.CASCADE, related_name='normalized'
    )
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='records'
    )

    # Emission data
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES)
    category = models.CharField(max_length=100)   # e.g. "Diesel", "Flight"
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    original_unit = models.CharField(max_length=50)  # e.g. "liters", "kWh"
    normalized_quantity = models.DecimalField(
        max_digits=15, decimal_places=4
    )  # Always in kg
    normalized_unit = models.CharField(
        max_length=10, default='kg'
    )
    co2_equivalent = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )  # kgCO2e

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Review workflow
    review_status = models.CharField(
        max_length=20, choices=REVIEW_CHOICES, default='pending'
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_records'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, null=True)

    # Flags
    is_suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(blank=True, null=True)
    is_edited = models.BooleanField(default=False)  # Manually edited?
    is_locked = models.BooleanField(default=False)  # Locked for audit?

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.scope} | {self.category} | {self.co2_equivalent} kgCO2e"


# ─── Model 6: AuditLog ─────────────────────────────
class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('upload', 'File Uploaded'),
        ('normalize', 'Record Normalized'),
        ('approve', 'Record Approved'),
        ('reject', 'Record Rejected'),
        ('flag', 'Record Flagged'),
        ('edit', 'Record Edited'),
        ('lock', 'Record Locked'),
    ]

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='audit_logs'
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    record = models.ForeignKey(
        NormalizedRecord, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"