from datetime import date
from urllib.parse import urlencode

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.timezone import localdate
from django.views.decorators.http import require_GET, require_http_methods

from .forms import DEFECT_LABELS, ShiftForm
from .models import DEFECTS
from .machines import WORKSHOP
from .reports import daily_production, machines_per_shift, weekly_report


def selected_day(request):
    value = request.GET.get("date")
    return date.fromisoformat(value) if value is not None else localdate()


@require_http_methods(["GET", "POST"])
def dashboard(request):
    try:
        day = selected_day(request)
        report = weekly_report(day)
    except (ValueError, OverflowError):
        return HttpResponseBadRequest("Choose a valid date in YYYY-MM-DD format.")
    form = ShiftForm(request.POST if request.method == "POST" else None, initial={"date": day})
    if request.method == "POST" and form.is_valid():
        shift = form.save()
        return redirect(reverse("dashboard") + "?" + urlencode({"date": shift.date, "saved": 1}))
    machine = request.GET.get("machine", "")
    machine_names = dict(WORKSHOP)
    for row in report["machines"]:
        code = row["machine"]
        row["display_name"] = machine_names.setdefault(code, code)
    if machine not in machine_names:
        machine = ""
    days, counts = daily_production(date.fromisoformat(report["start"]), machine)
    produced = sum(day["produced"] for day in days)
    rejected = sum(counts.values())
    reasons = [{"name": DEFECT_LABELS[DEFECTS[field]], "count": count,
                "share": 100 * count / rejected if rejected else 0}
               for field, count in counts.items()]
    leading_reasons = [reason for reason in reasons if rejected and reason["count"] == max(counts.values())]
    active_average, shift_count = machines_per_shift(report["start"], report["end"])
    for row in report["machines"]:
        row["reasons"] = [DEFECT_LABELS[reason] for reason in row["top_defects"]]
    return render(request, "tracker/dashboard.html", {
        "form": form, "report": report, "day": day.isoformat(),
        "adding_shift": request.GET.get("entry") == "1" or form.is_bound,
        "week_start": date.fromisoformat(report["start"]),
        "week_end": date.fromisoformat(report["end"]),
        "machine": machine, "machine_names": machine_names,
        "active_average": active_average, "shift_count": shift_count,
        "days": days, "reasons": reasons,
        "peak_output": max(day["produced"] for day in days),
        "selected_output_day": next((day["date"] for day in days if day["entries"]), days[0]["date"]),
        "top_reason": leading_reasons[0] if len(leading_reasons) == 1 else None,
        "produced": produced, "rejected": rejected, "accepted": produced - rejected,
        "yield_rate": 100 * (produced - rejected) / produced if produced else None,
        "saved": request.GET.get("saved") == "1" and not form.is_bound,
    })


@require_GET
def report_api(request):
    try:
        return JsonResponse(weekly_report(selected_day(request)))
    except (ValueError, OverflowError):
        return JsonResponse({"error": "Choose a valid date in YYYY-MM-DD format."}, status=400)
