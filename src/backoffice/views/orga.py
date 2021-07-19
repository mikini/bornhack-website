import logging

from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView

from camps.mixins import CampViewMixin
from profiles.models import Profile
from shop.models import OrderProductRelation
from teams.models import Team
from utils.models import OutgoingEmail

from ..mixins import OrgaTeamPermissionMixin

logger = logging.getLogger("bornhack.%s" % __name__)


class ApproveNamesView(CampViewMixin, OrgaTeamPermissionMixin, ListView):
    template_name = "approve_public_credit_names.html"
    context_object_name = "profiles"

    def get_queryset(self, **kwargs):
        return Profile.objects.filter(public_credit_name_approved=False).exclude(
            public_credit_name=""
        )


################################
# MERCHANDISE VIEWS


class MerchandiseOrdersView(CampViewMixin, OrgaTeamPermissionMixin, ListView):
    template_name = "orders_merchandise.html"

    def get_queryset(self, **kwargs):
        camp_prefix = "BornHack {}".format(timezone.now().year)

        return (
            OrderProductRelation.objects.filter(
                order__refunded=False,
                order__cancelled=False,
                product__category__name="Merchandise",
            )
            .filter(product__name__startswith=camp_prefix)
            .order_by("order")
        )


class MerchandiseToOrderView(CampViewMixin, OrgaTeamPermissionMixin, TemplateView):
    template_name = "merchandise_to_order.html"

    def get_context_data(self, **kwargs):
        camp_prefix = "BornHack {}".format(timezone.now().year)

        order_relations = OrderProductRelation.objects.filter(
            order__refunded=False,
            order__cancelled=False,
            product__category__name="Merchandise",
        ).filter(product__name__startswith=camp_prefix)

        merchandise_orders = {}
        for relation in order_relations:
            try:
                quantity = merchandise_orders[relation.product.name] + relation.quantity
                merchandise_orders[relation.product.name] = quantity
            except KeyError:
                merchandise_orders[relation.product.name] = relation.quantity

        context = super().get_context_data(**kwargs)
        context["merchandise"] = merchandise_orders
        return context


################################
# VILLAGE VIEWS


class VillageOrdersView(CampViewMixin, OrgaTeamPermissionMixin, ListView):
    template_name = "orders_village.html"

    def get_queryset(self, **kwargs):
        camp_prefix = "BornHack {}".format(timezone.now().year)

        return (
            OrderProductRelation.objects.filter(
                ticket_generated=False,
                order__paid=True,
                order__refunded=False,
                order__cancelled=False,
                product__category__name="Villages",
            )
            .filter(product__name__startswith=camp_prefix)
            .order_by("order")
        )


class VillageToOrderView(CampViewMixin, OrgaTeamPermissionMixin, TemplateView):
    template_name = "village_to_order.html"

    def get_context_data(self, **kwargs):
        camp_prefix = "BornHack {}".format(timezone.now().year)

        order_relations = OrderProductRelation.objects.filter(
            ticket_generated=False,
            order__paid=True,
            order__refunded=False,
            order__cancelled=False,
            product__category__name="Villages",
        ).filter(product__name__startswith=camp_prefix)

        village_orders = {}
        for relation in order_relations:
            try:
                quantity = village_orders[relation.product.name] + relation.quantity
                village_orders[relation.product.name] = quantity
            except KeyError:
                village_orders[relation.product.name] = relation.quantity

        context = super().get_context_data(**kwargs)
        context["village"] = village_orders
        return context


#########################################
# UPDATE AND RELEASE HELD OUTGOING EMAILS


class OutgoingEmailMassUpdateView(CampViewMixin, OrgaTeamPermissionMixin, FormView):
    """
    This view shows a list with forms to edit OutgoingEmail objects with hold=True
    """

    template_name = "outgoing_email_mass_update.html"

    def setup(self, *args, **kwargs):
        """Get emails with no team and emails with a team for the current camp."""
        super().setup(*args, **kwargs)
        self.queryset = OutgoingEmail.objects.filter(
            hold=True, responsible_team__isnull=True
        ).prefetch_related("responsible_team") | OutgoingEmail.objects.filter(
            hold=True, responsible_team__camp=self.camp
        ).prefetch_related(
            "responsible_team"
        )
        self.form_class = modelformset_factory(
            OutgoingEmail,
            fields=["subject", "text_template", "html_template", "hold"],
            min_num=self.queryset.count(),
            validate_min=True,
            max_num=self.queryset.count(),
            validate_max=True,
            extra=0,
        )

    def get_context_data(self, *args, **kwargs):
        """Include the formset in the context."""
        context = super().get_context_data(*args, **kwargs)
        context["formset"] = self.form_class(queryset=self.queryset)
        return context

    def form_valid(self, form):
        """Show a message saying how many objects were updated."""
        form.save()
        if form.changed_objects:
            messages.success(
                self.request, f"Updated {len(form.changed_objects)} OutgoingEmails"
            )
        return redirect(self.get_success_url())

    def get_success_url(self, *args, **kwargs):
        """Return to the backoffice index."""
        return reverse("backoffice:index", kwargs={"camp_slug": self.camp.slug})


######################
# IRCBOT RELATED VIEWS
class IrcOverView(CampViewMixin, OrgaTeamPermissionMixin, ListView):
    model = Team
    template_name = "irc_overview.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(
                public_irc_channel_name__isnull=True,
                private_irc_channel_name__isnull=True,
            )
        )
