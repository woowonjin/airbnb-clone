from django.db import models
from django.utils import timezone
from core import models as core_models
import datetime


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
