
### URLs
#### **Redirecting back to same page** (e.g after submitting profile on same profile page.)
* **Method 1**: Setting and absolute url and using ```self.object.get_absolute_url()```
* **request.META.get("HTTP_REFERER")** the request.META is a dictionary containing all available HTTP headers.
* Get is used to safely retrieve the referer so if it's not the it returns None, instead of a key error.
* When doing this a fallback is advise, incase the referer is not found. e.g ```redirectrequest.Meta.get("HTTP_REFERER") or self.object.get_absolute_url() )```


### CBVs Architecture. (manual vs built in rendering.)
* Built in rendering comes with mixins, which are not available for manual rendering.
```commandline
**Barebone View class**
class Register(View):
    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        return render(request, "users/register.html", context={"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, message="Account created successful")
            return redirect("auth:profile", kwargs={"pk":new_user.id})
        return render(request, "users/register.html", context={"form": form})


```
* Using this barebone view gives no rendering logic out of the box.
* We are to manually call render in both get() nad post() hence repetition
* This is more recommended when full control is to be taken.

* Using more specific views like DetailView which itself inherit several mixins
* **SingleObjectMixin (fetches the object)**, **TemplateResponseMixin (handles rendering)**, **BaseDetailView (ties it all together)**
* Now the get and post methods here can then use the magic method ```**render_to_response(context)**```. It uses the template_name and context to render the response without needing to call render
* We are also provided the ```get_context_data()``` method for free which merges your custom context with the default one.

```commandline
f get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        context["profile_owner"] = self.object.user

        # if owner or staff → add forms
        if request.user.is_authenticated and (
            request.user == self.object.user  # or request.user.is_staff
        ):
            context["user_form"] = UserUpdateForm(instance=self.object.user)
            context["profile_form"] = AdminProfileUpdateForm(instance=self.object)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Security check
        if not request.user.is_authenticated or request.user != self.object.user:
            return redirect(self.object.get_absolute_url())

        user_form = UserUpdateForm(request.POST, instance=self.object.user)
        profile_form = AdminProfileUpdateForm(
            request.POST, request.FILES, instance=self.object
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            previous_url = request.META.get("HTTP_REFERER")
            return redirect(previous_url or self.object.get_absolute_url())

        # Re-render with errors
        context = self.get_context_data(
            user_form=user_form,
            profile_form=profile_form
        )
        return self.render_to_response(context)

```
* This way no render repetition
* clean separation of concerns.
* We can override the get context data.