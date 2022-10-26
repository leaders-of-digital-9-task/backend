from dicom.models import Dicom
from rest_framework import serializers


class ListDicomSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="get_update_delete_dicom", lookup_field="slug"
    )
    file = serializers.FileField()

    class Meta:
        model = Dicom
        fields = ["file", "uploaded", "url"]

    def create(self, validated_data):
        return Dicom.objects.create(**validated_data, user=self.context["request"].user)


class DicomSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Dicom
        fields = ["file", "uploaded"]
