"""Общие настройки виджетов форм."""

from django import forms


def apply_bootstrap_widgets(form: forms.Form) -> None:
    """Добавить CSS-классы Bootstrap к полям формы."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.FileInput):
            css_class = "form-control"
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            css_class = "form-select"
        elif isinstance(widget, forms.CheckboxInput):
            css_class = "form-check-input"
        else:
            css_class = "form-control"
        existing = widget.attrs.get("class", "")
        if css_class not in existing.split():
            widget.attrs["class"] = f"{existing} {css_class}".strip()
