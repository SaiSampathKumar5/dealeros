from django.db import models


class Location(models.Model):
    location_id = models.CharField(max_length=20, unique=True)
    org_id = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=100, blank=True)


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=30, unique=True)
    location = models.ForeignKey(Location, to_field="location_id", null=True,
                                 on_delete=models.SET_NULL, related_name="a_records")
    location_raw = models.CharField(max_length=30, blank=True)
    event_date = models.DateField(null=True)
    category_code = models.CharField(max_length=20, blank=True)
    actor_id = models.CharField(max_length=20, null=True)
    base_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    adjustment = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    state = models.CharField(max_length=20, blank=True)


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=40, unique=True)
    record_ref_raw = models.CharField(max_length=50, blank=True)
    record_ref = models.CharField(max_length=30, null=True, db_index=True)  # NOT unique
    location = models.ForeignKey(Location, to_field="location_id", null=True,
                                 on_delete=models.SET_NULL, related_name="b_entries")
    location_raw = models.CharField(max_length=30, blank=True)
    recorded_on = models.DateField(null=True)
    value_raw = models.CharField(max_length=50, blank=True)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    label = models.CharField(max_length=100, blank=True)
