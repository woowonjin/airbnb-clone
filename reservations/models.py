from django.db import models
from django.utils import timezone
from core import models as core_models
import datetime
from . import managers


class BookedDay(core_models.TimeStampedModel):
    day = models.DateField()
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return f"{self.reservation.room} / {self.day}"


class Reservation(core_models.TimeStampedModel):
    """Reservation Definition"""

    STATUS_PENDING = "pending"
    STATUS_CONFIRM = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRM, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )
    objects = managers.CustomReservationManager()

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    default_time = timezone.now
    check_in = models.DateField(default=default_time)
    check_out = models.DateField(default=default_time)
    # check_in = models.DateField(default=datetime.datetime.now())
    # check_out = models.DateField(default=datetime.datetime.now())
    guest = models.ForeignKey(
        "users.User", related_name="reservations", on_delete=models.CASCADE, null=True
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = timezone.now().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        now = timezone.now().date()
        return now > self.check_out

    is_finished.boolean = True

    def save(self, *args, **kwargs):
        if self.pk is None:
            start = self.check_in
            end = self.check_out
            difference = end - start
            print("!!!!!!!!!")
            print("!!!!!!!!!")
            existing_booked_day = BookedDay.objects.filter(
                reservation__room=self.room, day__range=(start, end)
            ).exists()
            print("????????????")
            if not existing_booked_day:
                super().save(*args, **kwargs)
                for i in range(difference.days + 1):
                    day = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                print(">>>>>>>>>>>>>>>????!!!")
                return
            return super().save(*args, **kwargs)
