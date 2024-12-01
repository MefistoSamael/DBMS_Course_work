import base64
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError


def clean_image(image):
    if type(image) is str:
        return image
    valid_extensions = ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]
    print("IMAGE", image)
    if image.content_type not in valid_extensions:
        raise forms.ValidationError("Allowed format: jpg, jpeg, png, svg, webp.")
    image_file = image.read()
    return base64.b64encode(image_file).decode("utf-8")


def save_model_admin_panel(form, obj, change, service):
    image = form.cleaned_data.get("image", "")

    if not change and not image:
        raise ValidationError("Image cannot be empty")

    if image:
        obj.image = image

    if change:
        service.update(obj)
    else:
        service.create(obj)


def get_start_end_date(date_range):
    start_date, end_date = None, None

    if date_range:
        dates = date_range.split(" to ")
        if len(dates) == 1:
            start_date = end_date = dates[0]
        elif len(dates) == 2:
            start_date, end_date = dates
    return start_date, end_date


def prepare_check_in_and_out_dates(date_range):
    start_date, end_date = get_start_end_date(date_range)
    check_in_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    return check_in_date, check_out_date
