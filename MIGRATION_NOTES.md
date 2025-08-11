# Handling Non-Nullable Foreign Key Migrations

## The Problem
When adding a non-nullable foreign key to a model with existing data, Django requires a default value for existing rows. This is a common issue when:
1. Adding required foreign key fields to existing models
2. Splitting a monolithic app into multiple apps with user relationships

## Solution Pattern

### 1. Make the Field Nullable First
```python
# In your models.py
class YourModel(models.Model):
    # Instead of this:
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Do this first:
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
```

### 2. Create and Run Initial Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a Data Migration
```bash
# For housing app
python manage.py makemigrations --empty housing --name assign_house_owners

# For marketplace app
python manage.py makemigrations --empty marketplace --name assign_product_sellers
```

### 4. Edit the Data Migration
For each migration file created, add the data migration logic. Example for housing app:

```python
from django.db import migrations

def assign_owners(apps, schema_editor):
    House = apps.get_model('housing', 'House')
    User = apps.get_model('auth', 'User')
    
    # Get the first superuser or a specific user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.first()
    
    # Update all houses to be owned by this user
    House.objects.filter(owner__isnull=True).update(owner=admin_user)

class Migration(migrations.Migration):
    dependencies = [
        # Keep the auto-generated dependencies
    ]

    operations = [
        migrations.RunPython(assign_owners, reverse_code=migrations.RunPython.noop),
    ]
```

### 5. Run the Data Migration
```bash
python manage.py migrate
```

### 6. (Optional) Make the Field Required
After ensuring all records have a valid foreign key, you can make the field required by removing `null=True` and `blank=True` and creating a final migration.

## Best Practices
1. Always test migrations on a backup of your production data first
2. Consider using `get_user_model()` instead of direct User model import
3. Add proper error handling in your data migration
4. Document any assumptions made in the migration (e.g., which user is assigned as default)
