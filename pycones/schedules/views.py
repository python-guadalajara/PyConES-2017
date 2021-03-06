# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bleach
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from pycones.schedules.forms import PresentationForm
from pycones.schedules.helpers import export_to_pentabarf, export_to_xcal, export_to_icalendar, check_schedule_view
from pycones.schedules.models import Slot, Presentation, Day, Room


class ShowSchedule(View):
    """Shows the schedule of the event."""
    template_name = "schedule/show.html"

    def get(self, request):
        check_schedule_view(request)
        data = {"days": []}
        for day in Day.objects.all():
            data["days"].append({
                "tracks": day.track_set.order_by("order"),
                "date": day.date,
                "slots": day.slot_set.all().select_related(),
                "slot_groups": day.slot_groups(),
            })
        return render(request, self.template_name, data)


class ShowSlot(View):
    template_name = "schedule/details.html"

    def get(self, request, slot):
        check_schedule_view(request)
        try:
            slot_id = int(slot)
            slot = get_object_or_404(Slot, pk=slot_id)
            if slot.presentation.slug:
                return redirect(slot.get_absolute_url(), permanent=True)
        except ValueError:
            slot = get_object_or_404(Slot, presentation__slug=slot)
        data = {
            "slot": slot,
            "biographies": [
                mark_safe(bleach.clean(speaker.biography.rendered, 'script')) for speaker in slot.content.get_speakers()
            ]
        }
        return render(request, self.template_name, data)


class EditPresentation(LoginRequiredMixin, View):
    template_name = "schedule/presentations/edit.html"

    def get_login_url(self):
        return reverse("speakers:sign-in")

    def get(self, request, presentation_id):
        presentation = get_object_or_404(Presentation, pk=presentation_id)
        if request.user.speaker not in presentation.get_speakers():
            raise Http404()
        form = PresentationForm(instance=presentation)
        data = {
            "presentation": presentation,
            "form": form
        }
        return render(request, self.template_name, data)

    def post(self, request, presentation_id):
        presentation = get_object_or_404(Presentation, pk=presentation_id)
        if request.user.speaker not in presentation.get_speakers():
            raise Http404()
        form = PresentationForm(request.POST, request.FILES, instance=presentation)
        data = {
            "presentation": presentation,
            "form": form
        }
        if form.is_valid():
            form.save()
            messages.success(request, _("Datos actualizados correctamente"))
            return redirect(reverse("schedule:edit-presentation", kwargs={"presentation_id": presentation_id}))
        return render(request, self.template_name, data)


def pentabarf_view(request):
    """Download Pentabarf calendar file.
    :param request:
    """
    check_schedule_view(request)
    days = Day.objects.all()
    rooms = Room.objects.all()
    pentabarf_xml = export_to_pentabarf(days, rooms)
    return HttpResponse(pentabarf_xml, content_type="application/xml")


def xcal_view(request):
    """Download xCal file.
    :param request:
    """
    check_schedule_view(request)
    days = Day.objects.all()
    xcal_xml = export_to_xcal(days)
    return HttpResponse(xcal_xml, content_type="application/xml")


def icalendar_view(request):
    """Download iCalendar file.
    :param request:
    """
    check_schedule_view(request)
    days = Day.objects.all()
    calendar_text = export_to_icalendar(days)
    return HttpResponse(calendar_text, content_type="text/calendar")
