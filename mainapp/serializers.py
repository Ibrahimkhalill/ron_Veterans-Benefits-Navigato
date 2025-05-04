from rest_framework import serializers
from .models import VaForm, Document, OtherDocument
from authentications.serializers import CustomUserSerializer
from authentications.models import CustomUser

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'file', 'va_form']
        read_only_fields = ['va_form']

class VaFormSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    user = CustomUserSerializer(read_only=True)
  
    class Meta:
        model = VaForm
        fields = ['id', 'user', 'status', 'submission_date', 'fax_status', 'extra_data', 'documents']
        read_only_fields = ['submission_date', 'user']

class OtherDocumentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = OtherDocument
        fields = ['id', 'user', 'document_name', 'document_type', 'file', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user']