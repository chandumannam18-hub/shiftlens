from django.test import TestCase
from django.urls import reverse

from .models import Shift


class WorkshopTests(TestCase):
    def setUp(self):
        self.entry = dict(date="2026-11-23", machine="lathe-01", component="bush-20",
                          period="Day", produced=10, dimension=2, finish=0, other=0)

    def submit(self, **changes):
        return self.client.post(reverse("dashboard"), {**self.entry, **changes}, follow=True)

    def rows(self):
        return self.client.get(reverse("report-api"), {"date": "2026-11-24"}).json()["machines"]

    def test_weighted_rate_and_week_filter(self):
        self.submit()
        response = self.submit(date="2026-11-24", produced=90, finish=1)
        self.submit(date="2026-11-30", produced=12)
        self.submit(machine="lathe-02", produced=100)
        self.assertContains(response, "5.00%")
        self.assertEqual(self.rows()[0], {"machine": "LATHE-01", "produced": 100, "rejected": 5,
                                         "rate": 5.0, "top_defects": ["Out of tolerance"]})

    def test_invalid_counts_and_duplicate(self):
        self.assertContains(self.submit(produced=1), "Rejected parts cannot exceed")
        self.submit(dimension=-1)
        self.assertEqual(Shift.objects.count(), 0)
        self.submit()
        self.submit(machine="LATHE-01")
        self.assertEqual(Shift.objects.count(), 1)

    def test_zero_and_tied_defects(self):
        self.submit(machine="idle", produced=0, dimension=0)
        self.submit(finish=2)
        first, second = self.rows()
        self.assertEqual(first["top_defects"], ["Out of tolerance", "Surface finish"])
        self.assertIsNone(second["rate"])

    def test_bad_date_and_empty_week(self):
        self.assertEqual(self.rows(), [])
        self.assertEqual(self.client.get(reverse("report-api"), {"date": "bad"}).status_code, 400)

    def test_machine_labels_and_distinct_active_machines_per_shift(self):
        self.submit(machine="Semi-automatic lathe 1")
        self.submit(machine="Semi-automatic lathe 1", component="DIFFERENT-PART")
        self.submit(machine="CNC turning centre 1")
        self.submit(machine="Drilling machine", period="Night", produced=0, dimension=0)
        report = self.client.get(reverse("dashboard"), {"date": "2026-11-23", "machine": "10"})
        self.assertContains(report, "CNC turning centre 1")
        self.assertEqual(report.context["produced"], 10)
        self.assertEqual(report.context["active_average"], 1)
        self.assertEqual(report.context["shift_count"], 2)

    def test_daily_chart_and_reasons_follow_machine_selection(self):
        self.submit()
        self.submit(machine="second", produced=20, finish=3)
        report = self.client.get(reverse("dashboard"), {"date": "2026-11-25", "machine": "SECOND"}).context
        self.assertEqual((report["accepted"], report["rejected"]), (15, 5))
        self.assertEqual([item["count"] for item in report["reasons"]], [2, 3, 0])
        self.assertEqual([item["produced"] for item in report["days"]], [20, 0, 0, 0, 0, 0, 0])
        self.assertEqual(len(report["report"]["machines"]), 2)
