from django.contrib import admin
from .models import VaForm, Document, Contact, OtherDocument

# Inline admin for Document (to be displayed directly in VaForm admin)
class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    fields = ['document_type', 'file']
    readonly_fields = []

# VaForm Admin
class VaFormAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submission_date', 'fax_status', 'document_count')
    search_fields = ('user__email', 'status')
    list_filter = ('status', 'fax_status')
    inlines = [DocumentInline]

    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Documents'

# Document Admin
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('va_form', 'document_type', 'file')
    search_fields = ('va_form__user__email', 'document_type')
    list_filter = ('document_type',)

# Contact Admin
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('is_resolved', 'created_at')
    readonly_fields = ('created_at',)

# OtherDocument Admin
class OtherDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type','document_name', 'user', 'file', 'created_at', 'updated_at')
    search_fields = ('document_name', 'user__email')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

# Register the models
admin.site.register(VaForm, VaFormAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(OtherDocument, OtherDocumentAdmin)