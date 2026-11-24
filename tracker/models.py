from django.core.exceptions import ValidationError
from django.db import models

# Each rejected part is counted once under its primary defect.
DEFECTS = {
    "dimension": "Out of tolerance",
    "finish": "Surface finish",
    "other": "Other",
}


class Shift(models.Model):
    date = models.DateField()
    machine = models.CharField(max_length=40)
    component = models.CharField(max_length=60)
    period = models.CharField(max_length=8, choices=[("Day", "Day"), ("Night", "Night")])
    produced = models.PositiveIntegerField("Total parts produced")
    dimension = models.PositiveIntegerField("Out of tolerance", default=0)
    finish = models.PositiveIntegerField("Surface finish", default=0)
    other = models.PositiveIntegerField("Other rejects", default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["date", "period", "machine", "component"],
                                    name="one_component_total_per_shift"),
            models.CheckConstraint(
                condition=models.Q(produced__gte=models.F("dimension") + models.F("finish") + models.F("other")),
                name="rejects_within_production",
            ),
        ]

    def clean(self):
        counts = [getattr(self, name) for name in DEFECTS]
        if self.produced is not None and None not in counts and sum(counts) > self.produced:
            raise ValidationError("Rejected parts cannot exceed total parts produced.")
