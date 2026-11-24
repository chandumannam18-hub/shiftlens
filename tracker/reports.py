from datetime import timedelta

from django.db.models import Count, Q, Sum

from .models import DEFECTS, Shift


def machines_per_shift(start, end):
    shifts = (Shift.objects.filter(date__range=(start, end))
              .values("date", "period")
              .annotate(active=Count("machine", distinct=True, filter=Q(produced__gt=0))))
    counts = [shift["active"] for shift in shifts]
    return sum(counts) / len(counts) if counts else None, len(counts)


def weekly_report(day):
    monday = day - timedelta(days=day.weekday())
    sunday = monday + timedelta(days=6)
    sums = {f"{field}_sum": Sum(field) for field in ["produced", *DEFECTS]}
    totals = Shift.objects.filter(date__range=(monday, sunday)).values("machine").annotate(**sums)
    machines = []
    for row in totals:
        produced = row["produced_sum"]
        counts = {label: row[f"{field}_sum"] for field, label in DEFECTS.items()}
        rejected = sum(counts.values())
        machines.append({
            "machine": row["machine"], "produced": produced, "rejected": rejected,
            "rate": 100 * rejected / produced if produced else None,
            "top_defects": [label for label, count in counts.items() if count and count == max(counts.values())],
        })
    machines.sort(key=lambda item: (item["rate"] is None, -(item["rate"] or 0), item["machine"]))
    return {"start": monday.isoformat(), "end": sunday.isoformat(), "machines": machines}


def daily_production(monday, machine=None):
    sunday = monday + timedelta(days=6)
    shifts = Shift.objects.filter(date__range=(monday, sunday))
    if machine:
        shifts = shifts.filter(machine=machine)
    sums = {f"{field}_count": Sum(field) for field in DEFECTS}
    rows = shifts.values("date").annotate(total=Sum("produced"), entries=Count("pk"), **sums)
    by_day = {row["date"]: row for row in rows}
    reasons = dict.fromkeys(DEFECTS, 0)
    days = []
    for offset in range(7):
        day = monday + timedelta(days=offset)
        row = by_day.get(day, {})
        rejected = 0
        for field in DEFECTS:
            count = row.get(f"{field}_count", 0)
            reasons[field] += count
            rejected += count
        produced = row.get("total", 0)
        days.append({"date": day, "produced": produced, "accepted": produced - rejected,
                     "rejected": rejected, "entries": row.get("entries", 0)})
    return days, reasons
