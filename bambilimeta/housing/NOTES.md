### UserPassesTestMixin
* When inheriting from this mixin, ```test_func()``` is the heart of the mixin.
* Its where the logic to determine if a user can access a view is defined.
* It restrict access based on certain conditions. 
* If test fails, user is redirected 
* It returns a bool, as output ```True or False``` allowing passage.
* code example.
```commandline
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import UpdateView
from .models import Product

class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'price']
    template_name = 'product_update.html'

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.owner
```
* ```self.object()``` fetches the object being updated
* Test if user is product-owner, if ```True``` proceed, else access denied.
* By Default
* User is redirected to the login page if not authenticated.
* If the are authenticated, and test fails, they get a 404 Forbidden response
* Custom exceptions and urls can be provided.

### CreateView Inheritance tips
* When using a create view, if form class is not specified, django defaults to using the model if fields parameter is defined
* But for custom validation, widgets and layouts, form_parameter is the best bet.
* In essence form class is ;
* Need custom widgets or field ordering
* Override clean() or field-level validation
* Reuse the form in other places e.g., admin, or update view
* **The ```form_valid()```** method is called after form passes validation, but before object is saved.
* Ideal for extra logic, modification, Triggering side effects before saving (e.g., email, log event.)
* When a form fails django calls a **```form_invalid()```** method which can be overridened and customized to.

### ListView (**get_queryset and get _context_data**)
* **```query_set()```** Defines which object will be listed and passed to the template.
* It can be set directly ```model = House <br/> query_set = House.objects.filter(is_published=True)```
* or override the query set.
```commandline
def get_queryset(self):
    return House.objects.filter(owner=self.request.user)
```
* The result of ```queryset or get_queryset()``` is passed to the template as ```object_list or house_list```. Reason why we often loop.
* **```get_context_data()```** 
* Purpose is adding extra context to the template beyond the default object list.
* Example 
```commandline
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_title'] = "Available Houses"
    context['featured'] = House.objects.filter(is_featured=True)
    return context
```
* typical use include adding a title, a list of featured houses. user_info, sidebar data.
###### **Is the model compulsory?**
* By default when model is used, django;
```commandline
class HouseListView(ListView):
    model = House
```
* Automatically does ```House.objects.all()``` and passes it to the template as default queryset, ```house_list``` as context variable name
* If queryset or get_queryset() is defined, it overrides the default queryset and simply

```commandline
class HouseListView(ListView):
    queryset = House.objects.filter(is_published=True)
    

def get_queryset(self):
    return House.objects.filter(owner=self.request.user)
```
* django infers the model from the queryset, so we dont need to explicitly specify the model.
* but using both makes views more readable, explicit and self-documenting.
* Enable other mixins or generic behaviors that rely on model.

### *```annotate()```*
* Used to add calculated fields to each object in a queryset.
* It allows you to perform calculations (logics) on the fields of the model and add the result as a virtual field, which is not stored in the database.
* Some common use cases;
* count related objects, add flags (is_favorited, is_owner, has_access etc.), aggregate values like total_price, average_rating.
* My example;
```commandline
    def get_queryset(self):
        qs = House.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        house=OuterRef("pk")
                    )
                )
            )
        else:
            qs = qs.annotate(
                is_favorited=Value(
                    False, output_field=BooleanField()
                )
            )
        return qs
```
* Code Breakdown;
```commandline
qs = House.objects.all()

if self.request.user.is_authenticated:
    qs = qs.annotate(
        is_favorited=Exists(
            Favorite.objects.filter(
                user=self.request.user,
                house=OuterRef("pk")
            )
        )
    )
```
* Analyzing from inside out;
* Exist returns a boolean. It returns True if subquery has result, otherwise False.
* OuterRef("pk") refers to the pk of the outer House instance.
* So for each house django checks **Deos a Favorite exist for this user and this house**
* It avoids loading all favorite into memory for filtering, hence super efficient and SQL powered.
* Handling Anonymous Users;
```commandline
qs = qs.annotate(
    is_favorited=Value(False, output_field=BooleanField())
)
```
* Ensures unauthenticated users get a False value for is_favorited, keeping logic clean and consistent
* **Other tips (```annotate(num_images=Count("images"), annotate(total_price=Sum("price"), annotate(is_expensive=Case(), annotate(latest_offer=Subquery("offers.order_by("-created").first().price")), annotate(has_reviews=Exists(Review.ob))```)**
* OuterRef("pk") refers to the pk of the outer House instance, ```request.user.house``` is not use because it is static, but OuterRef("pk") is dynamic.
* Essentially we are annotating the queryset of house instances, and for each we check if a favorite exists for this specific user and this specific house.
* So a way is  needed  to reference each individual House.pk inside the subquery. That’s what OuterRef("pk") does—it dynamically plugs in the pk of the current House being processed.
* **Using ```self.request.user.house```**
* - It assumes the user has one house, which may not be true.
* - It doesn’t help when looping through many houses in a queryset
* - It’s static—it doesn’t change per row.
* ```OuterRef("pk")``` It captures the pk of each individual House instance as the queryset is evaluated.
* because am calling .annotate() on a queryset of House objects, OuterRef("pk") implicitly refers to the pk of each House in that queryset. That context is what makes OuterRef powerful and intuitive.
* orther fields can be used to, as long as the exist on the model being queried, (House) django will dynamically plug them into the subquery
```commandline
OuterRef("slug")
OuterRef("owner_id")
OuterRef("created_at")
```

### Catching Pages or Content for a time duration
* Caching is the process of storing expensive or frequently accessed data temporarily so that future requests can be served faster without hinting the database or recomputing ressults
* Django caching is often used to;
* Reduce database queries, speed up page reloads, lower server load
```commandline
hero_homes = cache.get("hero_home_list")  # Try to get cached data
if not hero_homes:
    hero_homes = list(House.objects.all()[:3])  # Query DB if cache is empty
    cache.set("hero_home_list", hero_homes, 900)  # Store result in cache for 900 seconds (15 mins)
context["hero_homes"] = hero_homes
```
* cache.get("hero_home_list"): Checks if the data is already cached. 
* If not cached:
* Queries the database for the first 3 houses.
* Stores the result in cache with a key "hero_home_list" and a timeout of 900 seconds.
* Sets the result in the context so it can be used in the template.
* Note **CACHE need to be set in settings.py**
* Common Use Cases
* Homepage data: Like your hero_homes, which rarely changes. 
* Expensive queries: Aggregations, joins, or large datasets. 
* API responses: To reduce external calls. 
* Fragments of templates: Using {% cache %} in templates.
*  Gotchas to Watch For 
* Cached data can become stale—you’ll need to invalidate or refresh it when the underlying data changes. 
* Be careful with per-user data—don’t cache personalized content globally. 
* Always set a timeout unless you plan to manually invalidate.
* Parts of template can be cached with the {% cache %} tag.
```commandline
{% load cache %}
{% cache 900 hero_home_list %}
    {% for house in hero_homes %}
        {{ house.name }}
    {% endfor %}
{% endcache %}
```
#### Cache Invalidation and Reshuffling
* Caching is great, but stale data is a real risk. will want to invalidate or refresh the cache when the underlying data changes—like when a new house is added or an existing one is updated.
* This can be done manually or using the cache framework.
* **```cache.clear('hero_home_list')```** clears all cached data, this can be done with signals or admin actions, when data changes
* **Automatic Invalidation with signals**

### **```dispatch()``**
* ```dispatch()``` is the entry point which decides which method to call (get(), post()) based on request type
* in the case of my HouseListView
```commandline
def dispatch(self, request, *args, **kwargs):
    messages.info(request, "Welcome to bambili rentals!")
    return super().dispatch(request, *args, **kwargs)
```
* We are injecting flash message before any logic runs
* It works for all request types (GET, POST, etc)
* Keeps view dry and centralized.
* Dispactch can be used to;
* logging page visits
* checking permissions
* inject context-wide messages
* Tracking analytics
* Redirecting based on conditions.
* sending notifications
* Example 
```commandline
def dispatch(self, request, *args, **kwargs):
    if request.user.is_authenticated and request.user.profile.is_banned:
        messages.error(request, "Your account is restricted.")
        return redirect("banned_notice")
    return super().dispatch(request, *args, **kwargs)
    
```

### Some parameters of LoginRequiredMixin
* login_url: The URL to redirect to if the user is not logged in
* redirect_field_name: The name of the get query parameter that stores the original destination
* example ```auth/login/?next=/house/create/```
* This ensures smooth user experience, users are sent back where the intended to go
* 