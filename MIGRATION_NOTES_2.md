### Incremental Migration with Null --> Populate --> NonNull
1. Backup database: This is done by dumping current data
```commandline
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup.json

```
2. Add the new fields and make all of the required ones nullable
3. Generate migrations, using `makemigrations` and `migrate`
4. Write a data migration to populate the new fields for all existing rows for each model
```commandline
python manage.py makemigrations --empty housing --name populate_new_house_fields
or 
python manage.py makemigrations --empty marketplace --name populate_product_fields

```
5. Edit this empty migration file to populate the new fields
```commandline
from django.db import migrations

def populate_product_fields(apps, schema_editor):
    Product = apps.get_model('marketplace', 'Product')
    for p in Product.objects.all():
        if p.category is None:
            p.category = "electronics"  # or "books", depending on your default
        if p.condition is None:
            p.condition = "used"
        if p.is_student_discount is None:
            p.is_student_discount = False
        if p.pickup_location is None:
            p.pickup_location = "On-campus"
        if p.delivery_available is None:
            p.delivery_available = False
        if p.warranty_period_months is None:
            p.warranty_period_months = 0
        p.save()

class Migration(migrations.Migration):
    dependencies = [
        ('marketplace', 'XXXX_auto'),
    ]

    operations = [
        migrations.RunPython(populate_product_fields, reverse_code=migrations.RunPython.noop),
    ]

```
6. Run the data migration
```commandline
python manage.py migrate    

```
7. Change the fields to be non-nullable in the models
8. Generate and apply the final migration
```commandline
python manage.py makemigrations
python manage.py migrate    

```
9. Test thoroughly to ensure everything works as expected
10. Clean up: Remove any temporary code