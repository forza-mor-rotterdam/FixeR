from django.db.models import QuerySet


class TaakQuerySet(QuerySet):
    def get_taken_recent(self, user):
        return self.order_by("-aangemaakt_op")
