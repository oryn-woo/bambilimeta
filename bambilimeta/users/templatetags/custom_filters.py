from django import template
from django.db import models

register = template.Library()

@register.filter
def class_name(value, include_app=False):
    """
    Returns the class name of any Python object.
    - For Django model instances: returns ModelName (or app_label.ModelName if include_app=True)
    - For QuerySets: returns the model's name
    - For RelatedManagers: returns related model's name
    - For plain Python objects: returns the Python class name
    """
    try:
        # Handle Django QuerySet
        if hasattr(value, 'model'):
            model = value.model
            return f"{model._meta.app_label}.{model.__name__}" if include_app else model.__name__

        # Handle RelatedManager (e.g., user.products)
        if hasattr(value, 'related_model'):
            model = value.related_model
            return f"{model._meta.app_label}.{model.__name__}" if include_app else model.__name__

        # Handle Django model instance
        if isinstance(value, models.Model):
            model = value.__class__
            return f"{model._meta.app_label}.{model.__name__}" if include_app else model.__name__

        # Fallback for any Python object
        return value.__class__.__name__
    except Exception:
        return ''



@register.filter
def get_any_attr(obj, attrs):
    """
    Tries multiple (possibly nested) attributes on an object.
    Usage: {{ obj|get_any_attr:"name,title,seller.name" }}
    """
    for attr in attrs.split(","):
        try:
            parts = attr.split(".")
            value = obj
            for p in parts:
                value = getattr(value, p, None)
                if value is None:
                    break
            if value:  # not None/empty string
                return value
        except Exception:
            continue
    return ""

