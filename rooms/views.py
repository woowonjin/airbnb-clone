from django.http import Http404
from django.views.generic import ListView, DetailView, View, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, reverse, redirect
from django_countries import countries
from django.core.paginator import Paginator
from . import models, forms
from users import mixins as user_mixins
from django.contrib.messages.views import SuccessMessageMixin


class HomeView(ListView):
    """HomeView Definition"""

    model = models.Room
    paginate_by = 12
    ordering = "created"
    paginate_orphans = 5
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RoomDetail(DetailView):
    """RoomDetail Definition"""

    model = models.Room


class SearchView(View):
    def get(self, request):

        country = request.GET.get("country")
        form = forms.SearchForm(request.GET)
        if country:

            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")
                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price"] = price

                if guests is not None:
                    filter_args["guests"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms"] = bedrooms

                if beds is not None:
                    filter_args["beds"] = beds

                if baths is not None:
                    filter_args["baths"] = baths

                if instant_book:
                    filter_args["instant_book"] = True

                if superhost:
                    filter_args["host__superhost"] = True

                rooms = models.Room.objects.filter(**filter_args)

                for amenity in amenities:
                    rooms = rooms.filter(amenities__pk=amenity.pk)

                for facility in facilities:
                    rooms = rooms.filter(amenities__pk=facility.pk)

                qs = rooms.order_by("-created")

                paginator = Paginator(qs, 3, orphans=1)
                page = request.GET.get("page", 1)
                rooms = paginator.get_page(page)
                page_num = paginator.num_pages
                get_copy = request.GET.copy()
                parameters = get_copy.pop("page", True) and get_copy.urlencode()
                return render(
                    request,
                    "rooms/search.html",
                    {
                        "form": form,
                        "rooms": rooms,
                        "page": page,
                        "page_num": page_num,
                        "current_url": parameters,
                    },
                )

        else:
            form = forms.SearchForm()
            rooms = models.Room.objects.filter()

        return render(request, "rooms/search.html", {"form": form},)


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted!!")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    fields = ("caption",)
    success_message = "Photo Updated!"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})
