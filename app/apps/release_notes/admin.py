from django.contrib import admin
from utils.diversen import truncate_tekst

from .models import ReleaseNote


class ReleaseNoteAdmin(admin.ModelAdmin):
    def korte_tekst(self, obj):
        return truncate_tekst(obj.beschrijving)

    list_display = ("titel", "korte_tekst", "aangemaakt_op", "publicatie_datum")
    search_fields = ("titel",)
    list_filter = ("aangemaakt_op", "publicatie_datum")
    ordering = ["aangemaakt_op"]
    # form = ReleaseNoteAanpassenForm
    korte_tekst.short_description = "Beschrijving"


admin.site.register(ReleaseNote, ReleaseNoteAdmin)
