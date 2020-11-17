from rest_framework import serializers


class CreateUpdateModelSerializer(serializers.ModelSerializer):

    def is_valid(self, raise_exception=False):
        if hasattr(self, 'initial_data'):
            payload_keys = self.initial_data.keys()
            serializer_fields = self.fields.keys()
            extra_fields = list(filter(lambda key: key not in serializer_fields, payload_keys))
            if extra_fields:
                raise serializers.ValidationError(f"Extra fields {extra_fields} in payload")
        return super().is_valid(raise_exception)
