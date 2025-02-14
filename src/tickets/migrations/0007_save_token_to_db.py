# Generated by Django 2.2.2 on 2019-07-18 18:52
from django.conf import settings
from django.db import migrations

from tickets.models import create_ticket_token


def save_tokens(apps, schema_editor):
    ShopTicket = apps.get_model("tickets", "ShopTicket")
    SponsorTicket = apps.get_model("tickets", "SponsorTicket")
    DiscountTicket = apps.get_model("tickets", "DiscountTicket")

    for model in (ShopTicket, SponsorTicket, DiscountTicket):

        for ticket in model.objects.all():
            token = create_ticket_token(
                "{_id}{secret_key}".format(
                    _id=ticket.uuid, secret_key=settings.SECRET_KEY
                ).encode("utf-8")
            )
            ticket.token = token
            ticket.save()


class Migration(migrations.Migration):

    dependencies = [("tickets", "0006_auto_20190616_1746")]

    operations = [migrations.RunPython(save_tokens)]
