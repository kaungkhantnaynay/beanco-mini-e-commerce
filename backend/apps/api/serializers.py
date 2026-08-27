from rest_framework import serializers


class ApiErrorSerializer(serializers.Serializer[dict[str, object]]):
    code = serializers.CharField()
    detail = serializers.CharField()
    fields = serializers.DictField(  # type: ignore[assignment]
        child=serializers.ListField(child=serializers.CharField())
    )
