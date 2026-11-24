from django import forms

from .models import Shift
from .machines import WORKSHOP


DEFECT_LABELS = {
    "Out of tolerance": "Wrong size",
    "Surface finish": "Poor surface finish",
    "Other": "Other reason",
}


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["date", "period", "machine", "component", "produced", "dimension", "finish", "other"]
        labels = {
            "date": "Shift date", "period": "Day or night", "machine": "Machine name",
            "component": "Part name or code", "produced": "Total parts made",
            "dimension": DEFECT_LABELS["Out of tolerance"],
            "finish": DEFECT_LABELS["Surface finish"], "other": DEFECT_LABELS["Other"],
        }
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "machine": forms.TextInput(attrs={"placeholder": "Choose or type a machine", "list": "workshop-machines"}),
            "component": forms.TextInput(attrs={"placeholder": "e.g. BUSH-20"}),
        }
        error_messages = {"__all__": {"unique_together": "You already saved this part for this machine and shift."}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, label_suffix="", **kwargs)
        self.fields["period"].choices = [("", "Select a shift"), *Shift._meta.get_field("period").choices]

    def clean_machine(self):
        value = self.cleaned_data["machine"]
        for code, name in WORKSHOP.items():
            if value.casefold() == name.casefold():
                return code
        return value.upper()

    def clean_component(self):
        return self.cleaned_data["component"].upper()
