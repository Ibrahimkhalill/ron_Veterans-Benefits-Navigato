from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('dd4', 'DD4 Document'),
        ('other', 'Other Document'),
        # Add more document types as needed
    ]
    
    va_form = models.ForeignKey('VaForm', on_delete=models.CASCADE, related_name='documents')  # Link back to VaForm
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/')
 
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.va_form.user.email}"

class VaForm(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vaform')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    extra_data = models.JSONField(default=dict, blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    fax_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f"VaForm for {self.user.email} - {self.status}"



class OtherDocument(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='other_documents'  # Unique related_name to avoid conflict with VaForm
    )
    document_name = models.CharField(max_length=300, blank=True, null=True)
    document_type = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='other_documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_name or 'Unnamed Document'} - {self.user.email}"



class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"
