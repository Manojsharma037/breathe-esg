import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from records.models import Tenant, DataUpload, RawRecord
from .serializers import DataUploadSerializer


class SAPUploadView(APIView):
    """
    SAP CSV file upload karo.
    Har row RawRecord mein save hogi.
    """

    def post(self, request):
        # 1. File aai ya nahi check karo
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Koi file nahi mili!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Tenant lo (abhi default first tenant)
        tenant = Tenant.objects.first()
        if not tenant:
            return Response(
                {'error': 'Pehle ek Tenant banao admin panel mein!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. DataUpload record banao
        upload = DataUpload.objects.create(
            tenant=tenant,
            source_type='sap',
            file_name=file.name,
            status='processing'
        )

        try:
            # 4. Pandas se CSV read karo
            df = pd.read_csv(file)

            # 5. Har row ko RawRecord mein save karo
            raw_records = []
            for index, row in df.iterrows():
                raw_records.append(
                    RawRecord(
                        upload=upload,
                        row_number=index + 1,
                        raw_data=row.to_dict(),
                        status='pending'
                    )
                )

            # 6. Sab ek saath save karo (fast)
            RawRecord.objects.bulk_create(raw_records)

            # 7. Upload status update karo
            upload.row_count = len(raw_records)
            upload.status = 'done'
            upload.save()

            return Response({
                'message': 'SAP data successfully upload hua!',
                'upload_id': upload.id,
                'rows_saved': len(raw_records),
                'file_name': file.name
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Kuch bhi galat hua toh
            upload.status = 'failed'
            upload.error_message = str(e)
            upload.save()

            return Response(
                {'error': f'File process nahi hui: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UtilityUploadView(APIView):
    """
    Utility CSV file upload karo.
    Electricity meter data save hoga.
    """

    def post(self, request):
        # 1. File check karo
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Koi file nahi mili!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Tenant lo
        tenant = Tenant.objects.first()
        if not tenant:
            return Response(
                {'error': 'Pehle ek Tenant banao admin panel mein!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. DataUpload record banao
        upload = DataUpload.objects.create(
            tenant=tenant,
            source_type='utility',  # UTILITY hardcoded
            file_name=file.name,
            status='processing'
        )

        try:
            # 4. Pandas se CSV padho
            df = pd.read_csv(file)

            # 5. Required columns check karo
            required_columns = [
                'METER_ID', 'KWH_CONSUMED', 
                'BILLING_PERIOD_START', 'BILLING_PERIOD_END'
            ]
            missing = [
                col for col in required_columns 
                if col not in df.columns
            ]
            if missing:
                upload.status = 'failed'
                upload.error_message = f'Missing columns: {missing}'
                upload.save()
                return Response(
                    {'error': f'CSV mein ye columns nahi hain: {missing}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 6. Har row RawRecord mein save karo
            raw_records = []
            for index, row in df.iterrows():
                raw_records.append(
                    RawRecord(
                        upload=upload,
                        row_number=index + 1,
                        raw_data=row.to_dict(),
                        status='pending'
                    )
                )

            RawRecord.objects.bulk_create(raw_records)

            # 7. Upload complete karo
            upload.row_count = len(raw_records)
            upload.status = 'done'
            upload.save()

            return Response({
                'message': 'Utility data successfully upload hua!',
                'upload_id': upload.id,
                'rows_saved': len(raw_records),
                'file_name': file.name
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            upload.status = 'failed'
            upload.error_message = str(e)
            upload.save()
            return Response(
                {'error': f'File process nahi hui: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  

import json

class TravelUploadView(APIView):
    """
    Travel JSON file upload karo.
    Flights, hotels, ground transport save hoga.
    """

    def post(self, request):
        # 1. File check karo
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Koi file nahi mili!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Tenant lo
        tenant = Tenant.objects.first()
        if not tenant:
            return Response(
                {'error': 'Pehle ek Tenant banao!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. DataUpload record banao
        upload = DataUpload.objects.create(
            tenant=tenant,
            source_type='travel',
            file_name=file.name,
            status='processing'
        )

        try:
            # 4. JSON file padho
            data = json.loads(file.read())

            # 5. List hai ya nahi check karo
            if not isinstance(data, list):
                upload.status = 'failed'
                upload.error_message = 'JSON must be a list of records'
                upload.save()
                return Response(
                    {'error': 'JSON file mein list honi chahiye!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 6. Har record RawRecord mein save karo
            raw_records = []
            for index, record in enumerate(data):
                raw_records.append(
                    RawRecord(
                        upload=upload,
                        row_number=index + 1,
                        raw_data=record,
                        status='pending'
                    )
                )

            RawRecord.objects.bulk_create(raw_records)

            # 7. Upload complete karo
            upload.row_count = len(raw_records)
            upload.status = 'done'
            upload.save()

            return Response({
                'message': 'Travel data successfully upload hua!',
                'upload_id': upload.id,
                'rows_saved': len(raw_records),
                'file_name': file.name
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError:
            upload.status = 'failed'
            upload.save()
            return Response(
                {'error': 'Valid JSON file nahi hai!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            upload.status = 'failed'
            upload.error_message = str(e)
            upload.save()
            return Response(
                {'error': f'File process nahi hui: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

from .services.normalizer import run_normalization

class NormalizeView(APIView):
    """
    Saare pending RawRecords normalize karo
    """
    def post(self, request):
        tenant = Tenant.objects.first()
        if not tenant:
            return Response(
                {'error': 'Tenant nahi mila!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = run_normalization(tenant)

        return Response({
            'message': 'Normalization complete!',
            'processed': results['processed'],
            'failed': results['failed'],
            'suspicious': results['suspicious']
        }, status=status.HTTP_200_OK)
    

from records.models import NormalizedRecord, AuditLog
from .serializers import NormalizedRecordSerializer
from django.utils import timezone
from django.db.models import Sum, Count


# ─── Records List API ───────────────────────────────
class RecordsListView(APIView):
    """
    Saare NormalizedRecords list karo.
    Filter: review_status, scope, source_type
    """
    def get(self, request):
        tenant = Tenant.objects.first()
        records = NormalizedRecord.objects.filter(
            tenant=tenant
        ).order_by('-created_at')

        # Filters
        review_status = request.query_params.get('review_status')
        scope = request.query_params.get('scope')
        source_type = request.query_params.get('source_type')

        if review_status:
            records = records.filter(review_status=review_status)
        if scope:
            records = records.filter(scope=scope)
        if source_type:
            records = records.filter(
                raw_record__upload__source_type=source_type
            )

        serializer = NormalizedRecordSerializer(records, many=True)
        return Response(serializer.data)


# ─── Approve API ────────────────────────────────────
class ApproveRecordView(APIView):
    """
    Record approve karo — analyst ne review kar liya
    """
    def post(self, request, pk):
        try:
            record = NormalizedRecord.objects.get(pk=pk)
        except NormalizedRecord.DoesNotExist:
            return Response(
                {'error': 'Record nahi mila!'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Locked record change nahi ho sakta
        if record.is_locked:
            return Response(
                {'error': 'Record locked hai — audit ke baad change nahi ho sakta!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(username='admin').first()

        # Approve karo
        record.review_status = 'approved'
        record.reviewed_by = admin_user
        record.reviewed_at = timezone.now()
        record.review_note = request.data.get('note', '')
        record.save()

        # AuditLog banao
        AuditLog.objects.create(
            tenant=record.tenant,
            user=admin_user,
            action='approve',
            record=record,
            note=f'Record approved: {record.category} - {record.co2_equivalent} kgCO2e'
        )

        return Response({
            'message': f'Record #{pk} approved!',
            'review_status': 'approved',
            'category': record.category,
            'co2_equivalent': str(record.co2_equivalent)
        })


# ─── Reject API ─────────────────────────────────────
class RejectRecordView(APIView):
    """
    Record reject karo — kuch galat lag raha hai
    """
    def post(self, request, pk):
        try:
            record = NormalizedRecord.objects.get(pk=pk)
        except NormalizedRecord.DoesNotExist:
            return Response(
                {'error': 'Record nahi mila!'},
                status=status.HTTP_404_NOT_FOUND
            )

        if record.is_locked:
            return Response(
                {'error': 'Record locked hai!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(username='admin').first()

        # Reject karo
        record.review_status = 'rejected'
        record.reviewed_by = admin_user
        record.reviewed_at = timezone.now()
        record.review_note = request.data.get('note', '')
        record.save()

        # AuditLog banao
        AuditLog.objects.create(
            tenant=record.tenant,
            user=admin_user,
            action='reject',
            record=record,
            note=f'Record rejected: {record.category} - {record.co2_equivalent} kgCO2e'
        )

        return Response({
            'message': f'Record #{pk} rejected!',
            'review_status': 'rejected',
            'category': record.category,
        })


# ─── Dashboard Stats API ────────────────────────────
class DashboardStatsView(APIView):
    """
    Dashboard ke liye summary stats
    """
    def get(self, request):
        tenant = Tenant.objects.first()
        records = NormalizedRecord.objects.filter(tenant=tenant)

        # Counts
        total = records.count()
        pending = records.filter(review_status='pending').count()
        approved = records.filter(review_status='approved').count()
        rejected = records.filter(review_status='rejected').count()
        suspicious = records.filter(review_status='suspicious').count()

        # CO2 by Scope
        scope1_co2 = records.filter(scope='scope1').aggregate(
            total=Sum('co2_equivalent')
        )['total'] or 0

        scope2_co2 = records.filter(scope='scope2').aggregate(
            total=Sum('co2_equivalent')
        )['total'] or 0

        scope3_co2 = records.filter(scope='scope3').aggregate(
            total=Sum('co2_equivalent')
        )['total'] or 0

        return Response({
            'total_records': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'suspicious': suspicious,
            'co2_by_scope': {
                'scope1': round(float(scope1_co2), 2),
                'scope2': round(float(scope2_co2), 2),
                'scope3': round(float(scope3_co2), 2),
                'total': round(
                    float(scope1_co2 + scope2_co2 + scope3_co2), 2
                )
            }
        })