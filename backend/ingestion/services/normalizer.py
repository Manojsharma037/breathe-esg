from decimal import Decimal
from records.models import RawRecord, NormalizedRecord
from django.utils import timezone

# ─── Emission Factors ───────────────────────────────
EMISSION_FACTORS = {
    'diesel':        Decimal('2.65'),   # kgCO2e per liter
    'petrol':        Decimal('2.31'),   # kgCO2e per liter
    'natural_gas':   Decimal('2.04'),   # kgCO2e per m3
    'electricity':   Decimal('0.91'),   # kgCO2e per kWh
    'flight_economy': Decimal('0.16'),  # kgCO2e per km
    'flight_business': Decimal('0.43'), # kgCO2e per km
    'hotel':         Decimal('31.0'),   # kgCO2e per night
    'ground':        Decimal('0.21'),   # kgCO2e per km
}


# ─── SAP Normalizer ─────────────────────────────────
def normalize_sap_record(raw_record):
    """
    SAP raw data ko NormalizedRecord mein convert karo.
    Scope 1 — Direct fuel combustion
    """
    data = raw_record.raw_data

    # Find Fuel type — In lowercase
    fuel_type = str(data.get('FUEL_TYPE', '')).lower().strip()
    fuel_type = fuel_type.replace(' ', '_')

    # Find Quantity
    try:
        quantity = Decimal(str(data.get('QUANTITY', 0)))
    except:
        quantity = Decimal('0')

    # Find Unit
    unit = str(data.get('UNIT', 'L')).upper()

    # find Emission factor 
    factor = EMISSION_FACTORS.get(fuel_type)
    if not factor:
        # Unknown fuel type
        raw_record.status = 'failed'
        raw_record.error_message = f'Unknown fuel type: {fuel_type}'
        raw_record.save()
        return None

    # CO2 calculate 
    co2 = quantity * factor

    # Make NormalizedRecord
    normalized = NormalizedRecord.objects.create(
        raw_record=raw_record,
        tenant=raw_record.upload.tenant,
        scope='scope1',
        category=fuel_type.capitalize(),
        quantity=quantity,
        original_unit=unit,
        normalized_quantity=quantity,
        normalized_unit='kg',
        co2_equivalent=co2,
        period_start=timezone.now().date(),
        period_end=timezone.now().date(),
        review_status='pending'
    )

    # RawRecord update
    raw_record.status = 'normalized'
    raw_record.save()

    return normalized


# ─── Utility Normalizer ──────────────────────────────
def normalize_utility_record(raw_record):
    """
    Utility raw data ko NormalizedRecord mein convert karo.
    Scope 2 — Indirect electricity emissions
    """
    data = raw_record.raw_data

    # Find kWh 
    try:
        kwh = Decimal(str(data.get('KWH_CONSUMED', 0)))
    except:
        kwh = Decimal('0')

    # CO2 calculate
    factor = EMISSION_FACTORS['electricity']
    co2 = kwh * factor

    # Find Period
    from datetime import datetime
    try:
        period_start = datetime.strptime(
            data.get('BILLING_PERIOD_START', ''), '%d-%m-%Y'
        ).date()
        period_end = datetime.strptime(
            data.get('BILLING_PERIOD_END', ''), '%d-%m-%Y'
        ).date()
    except:
        period_start = timezone.now().date()
        period_end = timezone.now().date()

    # NormalizedRecord
    normalized = NormalizedRecord.objects.create(
        raw_record=raw_record,
        tenant=raw_record.upload.tenant,
        scope='scope2',
        category='Electricity',
        quantity=kwh,
        original_unit='kWh',
        normalized_quantity=kwh,
        normalized_unit='kWh',
        co2_equivalent=co2,
        period_start=period_start,
        period_end=period_end,
        review_status='pending'
    )

    raw_record.status = 'normalized'
    raw_record.save()

    return normalized


# ─── Travel Normalizer ──────────────────────────────
def normalize_travel_record(raw_record):
    """
    Travel raw data ko NormalizedRecord mein convert karo.
    Scope 3 — Value chain emissions
    """
    data = raw_record.raw_data
    travel_type = str(data.get('travel_type', '')).lower()

    # Flight
    if travel_type == 'flight':
        try:
            distance = Decimal(str(data.get('distance_km', 0)))
        except:
            distance = Decimal('0')

        cabin = str(data.get('cabin_class', 'economy')).lower()
        if cabin == 'business':
            factor = EMISSION_FACTORS['flight_business']
        else:
            factor = EMISSION_FACTORS['flight_economy']

        co2 = distance * factor
        category = f'Flight ({cabin})'
        quantity = distance
        unit = 'km'

    # Hotel
    elif travel_type == 'hotel':
        try:
            nights = Decimal(str(data.get('nights', 1)))
        except:
            nights = Decimal('1')

        factor = EMISSION_FACTORS['hotel']
        co2 = nights * factor
        category = 'Hotel'
        quantity = nights
        unit = 'nights'

    # Ground transport
    elif travel_type == 'ground':
        try:
            distance = Decimal(str(data.get('distance_km', 0)))
        except:
            distance = Decimal('0')

        factor = EMISSION_FACTORS['ground']
        co2 = distance * factor
        category = 'Ground Transport'
        quantity = distance
        unit = 'km'

    else:
        raw_record.status = 'failed'
        raw_record.error_message = f'Unknown travel type: {travel_type}'
        raw_record.save()
        return None

    # NormalizedRecord
    normalized = NormalizedRecord.objects.create(
        raw_record=raw_record,
        tenant=raw_record.upload.tenant,
        scope='scope3',
        category=category,
        quantity=quantity,
        original_unit=unit,
        normalized_quantity=quantity,
        normalized_unit=unit,
        co2_equivalent=co2,
        period_start=timezone.now().date(),
        period_end=timezone.now().date(),
        review_status='pending'
    )

    raw_record.status = 'normalized'
    raw_record.save()

    return normalized


# ─── Suspicious Detection ───────────────────────────
def check_suspicious(normalized_record):
    """
    Agar value 3x average se zyada hai toh suspicious flag karo
    """
    category = normalized_record.category
    tenant = normalized_record.tenant

    # Same category ke saare records ka average nikalo
    same_category = NormalizedRecord.objects.filter(
        tenant=tenant,
        category=category
    ).exclude(id=normalized_record.id)

    if same_category.count() < 2:
        # Kam records hain — compare nahi kar sakte
        return

    # Average calculate
    total = sum([r.co2_equivalent for r in same_category])
    average = total / same_category.count()

    # 3x se zyada hai?
    if normalized_record.co2_equivalent > average * 3:
        normalized_record.is_suspicious = True
        normalized_record.suspicious_reason = (
            f'Value {normalized_record.co2_equivalent} kgCO2e is '
            f'more than 3x average ({average:.2f} kgCO2e) '
            f'for category {category}'
        )
        normalized_record.review_status = 'suspicious'
        normalized_record.save()


# ─── Main Function ──────────────────────────────────
def run_normalization(tenant):
    """
    Saare pending RawRecords normalize karo
    """
    # Sirf pending records lo
    pending_records = RawRecord.objects.filter(
        upload__tenant=tenant,
        status='pending'
    )

    results = {
        'processed': 0,
        'failed': 0,
        'suspicious': 0
    }

    for raw_record in pending_records:
        source_type = raw_record.upload.source_type

        # normalized based on source type
        if source_type == 'sap':
            normalized = normalize_sap_record(raw_record)
        elif source_type == 'utility':
            normalized = normalize_utility_record(raw_record)
        elif source_type == 'travel':
            normalized = normalize_travel_record(raw_record)
        else:
            results['failed'] += 1
            continue

        if normalized:
            # Suspicious check
            check_suspicious(normalized)
            if normalized.is_suspicious:
                results['suspicious'] += 1
            results['processed'] += 1
        else:
            results['failed'] += 1

    return results
