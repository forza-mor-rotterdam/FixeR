from rest_framework.relations import (
    HyperlinkedRelatedField as OriginalHyperlinkedRelatedField,
)


class HyperlinkedRelatedField(OriginalHyperlinkedRelatedField):
    def to_internal_value(self, data):
        # except urls with or without trailing slash
        if not data.endswith("/"):
            data = f"{data}/"
        return super().to_internal_value(data)
