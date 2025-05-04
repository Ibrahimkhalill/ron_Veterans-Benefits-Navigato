from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import json
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pdfrw import PdfReader, PdfWriter, PdfDict
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_va_form(request):
    """
    User submits a VA form with documents and extra JSON data.
    """
    data = request.data.copy()
    data['user'] = request.user.id

    # Handle stringified JSON if necessary
    extra_data = data.get('extra_data')
    if isinstance(extra_data, str):
        try:
            data['extra_data'] = json.loads(extra_data)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON in extra_data'}, status=400)

    serializer = VaFormSerializer(data=data, files=request.FILES)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def va_form_list(request):
        # Fetch all VaForms for the authenticated user
        va_forms = VaForm.objects.all()
        serializer = VaFormSerializer(va_forms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_va_form_status(request, form_id):
    """
    Update the status of a VA form (admin use).
    """
    vaform = get_object_or_404(VaForm, id=form_id)

    new_status = request.data.get('status')
    if new_status not in dict(VaForm.STATUS_CHOICES):
        return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

    vaform.status = new_status
    vaform.save()
    return Response({
        'detail': 'Status updated successfully.',
        'status': vaform.status
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_va_form(request, form_id):
    """
    Delete a VA form by ID (only the owner can delete).
    """
    vaform = get_object_or_404(VaForm, id=form_id, user=request.user)
    vaform.delete()
    return Response({'detail': 'VA Form deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def other_document_list(request):
    other_documents = OtherDocument.objects.filter(user=request.user)
    serializer = OtherDocumentSerializer(other_documents, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



import os
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject
from django.conf import settings

from openai import OpenAI
import os
from dotenv import load_dotenv
from mainapp.main_brain import generate_full_va_form

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUMMARY_API_KEY"))  # Load your OpenAI API key from environment variables


def generate_notation(form_data):
    prompt = f"Create a summary report for the following VA form data:\n{form_data}"
    try:
        # Call OpenAI's GPT model
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a summarizer assistant that only summarizes VA forms."},
            {"role": "user", "content": prompt}
        ],
        )
        # Extract and return the assistant's response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"



# @csrf_exempt
# def submit_form_api(request):
#     if request.method != 'POST':
#         return HttpResponse("Invalid request method", status=400)

#     try:
#         data = json.loads(request.body)
        
#         print("Received data:", data)
        
#         generate_summary_response = generate_summary(data)
#         print("Generated summary:", generate_summary_response)
#         # Save the summary to a file or database as needed
        
        
        

#         def get_digits(value):
#             return value.replace('-', '')

#         def split_date(value):
#             return value.split('/') if value else []

#         # Pre-process segmented fields
#         veteran_ssn = get_digits(data.get('veteran_ssn', ''))
#         veteran_dob = split_date(data.get('veteran_dob', ''))
#         mailing_zip = get_digits(data.get('mailing_address_zip', ''))
#         phone = get_digits(data.get('telephone_number', ''))

#         claimant_ssn = get_digits(data.get('claimant_ssn', ''))
#         claimant_dob = split_date(data.get('claimant_dob', ''))
#         claimant_zip = get_digits(data.get('claimant_mailing_address_zip', ''))
#         claimant_phone = get_digits(data.get('claimant_telephone_number', ''))
#         date_signed = split_date(data.get('date_signed', ''))

#         # Map form fields
#         field_mapping = {
#             'Veterans_First_Name[0]': data.get('veteran_first_name', ''),
#             'Veterans_Last_Name[0]': data.get('veteran_last_name', ''),
#             'Veterans_Middle_Initial1[0]': data.get('veteran_middle_initial', ''),
#             'Veterans_Social_SecurityNumber_FirstThreeNumbers[0]': veteran_ssn[:3],
#             'Veterans_Social_SecurityNumber_SecondTwoNumbers[0]': veteran_ssn[3:5],
#             'VeteransSocialSecurityNumber_LastFourNumbers[0]': veteran_ssn[5:9],
#             'DOB_Month[0]': veteran_dob[0] if len(veteran_dob) > 0 else '',
#             'DOB_Day[0]': veteran_dob[1] if len(veteran_dob) > 1 else '',
#             'DOB_Year[0]': veteran_dob[2] if len(veteran_dob) > 2 else '',
#             'VA_File_Number[0]': data.get('va_file_number', ''),
#             'Veterans_Service_Number[0]': data.get('veteran_service_number', ''),
#             'Mailing_Address_NumberAndStreet[0]': data.get('mailing_address_number_and_street', ''),
#             'Mailing_Address_ApartmentOrUnitNumber[0]': data.get('mailing_address_apartment_or_unit', ''),
#             'Mailing_Address_City[0]': data.get('mailing_address_city', ''),
#             'Mailing_Address_StateOrProvince[0]': data.get('mailing_address_state', ''),
#             'Mailing_Address_Country[0]': data.get('mailing_address_country', ''),
#             'MailingAddress_ZIPOrPostalCode_FirstFiveNumbers[0]': mailing_zip[:5],
#             'MailingAddress_ZIPOrPostalCode_LastFourNumbers[0]': mailing_zip[5:9],
#             'Telephone_Number_FirstThreeNumbers[0]': phone[:3],
#             'Telephone_Number_SecondThreeNumbers[0]': phone[3:6],
#             'Telephone_Number_LastFourNumbers[0]': phone[6:10],
#             'International_Phone_Number[0]': data.get('international_phone_number', ''),
#             'EMAIL_ADDRESS[0]': data.get('email_address', ''),
#             'COMPENSATION[0]': '/1',
#             'PENSION[0]': '/1',
#             'SURVIVORS_PENSION_AND_OR_DEPENDENCY_AND_INDEMNITY_COMPENSATION_DIC[0]': '/1',
#             # For additional user consent or selections
#             'CheckBox1[0]': '/1',
#             'CheckBox1[1]': '/1',
#             'RadioButtonList[1]': '/5',
#             'Date_Signed_Month[0]': date_signed[0] if len(date_signed) > 0 else '',
#             'Date_Signed_Day[0]': date_signed[1] if len(date_signed) > 1 else '',
#             'Date_Signed_Year[0]': date_signed[2] if len(date_signed) > 2 else '',
#             'Name_Of_Attorney_Agent_Or_Veterans_Service_Organization_VS[0]': data.get('name_of_attorney_or_vso', ''),

#             # Claimant Fields
#             'ClaimantsFirstName[0]': data.get('claimant_first_name', ''),
#             'ClaimantsLastName[0]': data.get('claimant_last_name', ''),
#             'ClaimantsMiddleInitial1[0]': data.get('claimant_middle_initial', ''),
#             'ClaimantsSocialSecurityNumber_FirstThreeNumbers[0]': claimant_ssn[:3],
#             'ClaimantsSocialSecurityNumber_SecondTwoNumbers[0]': claimant_ssn[3:5],
#             'ClaimantsSocialSecurityNumber_LastFourNumbers[0]': claimant_ssn[5:9],
#             'DOB_Month[1]': claimant_dob[0] if len(claimant_dob) > 0 else '',
#             'DOB_Day[1]': claimant_dob[1] if len(claimant_dob) > 1 else '',
#             'DOB_Year[1]': claimant_dob[2] if len(claimant_dob) > 2 else '',
#             'VA_File_Number[1]': data.get('claimant_va_file_number', ''),
#             'RelationshipToVeteranOther_Specify[0]': data.get('relationship_to_veteran', ''),
#             'Mailing_Address_NumberAndStreet[1]': data.get('claimant_mailing_address_number_and_street', ''),
#             'Mailing_Address_ApartmentOrUnitNumber[1]': data.get('claimant_mailing_address_apartment_or_unit', ''),
#             'Mailing_Address_City[1]': data.get('claimant_mailing_address_city', ''),
#             'Mailing_Address_StateOrProvince[1]': data.get('claimant_mailing_address_state', ''),
#             'Mailing_Address_Country[1]': data.get('claimant_mailing_address_country', ''),
#             'MailingAddress_ZIPOrPostalCode_FirstFiveNumbers[1]': claimant_zip[:5],
#             'MailingAddress_ZIPOrPostalCode_LastFourNumbers[1]': claimant_zip[5:9],
#             'Telephone_Number_FirstThreeNumbers[1]': claimant_phone[:3],
#             'Telephone_Number_SecondThreeNumbers[1]': claimant_phone[3:6],
#             'Telephone_Number_LastFourNumbers[1]': claimant_phone[6:10],
#             'ClaimantsInternational_Phone_Number[0]': data.get('claimant_international_phone_number', ''),
#             'ClaimantsEMAIL_ADDRESS[0]': data.get('claimant_email_address', ''),
            
#         }

#         # File paths
#         input_pdf = os.path.join(settings.STATICFILES_DIRS[0], 'pdfs', 'VBA-21-0966-ARE.pdf')
#         output_filename = f'filled_{veteran_ssn}.pdf'
#         output_pdf = os.path.join(settings.MEDIA_ROOT, output_filename)

#         reader = PdfReader(input_pdf)
#         writer = PdfWriter()

#         for page in reader.pages:
#             writer.add_page(page)

#         # Copy AcroForm + set NeedAppearances
#         if '/AcroForm' in reader.trailer['/Root']:
#             acro_form = reader.trailer['/Root']['/AcroForm']
#             writer._root_object.update({
#                 NameObject('/AcroForm'): writer._add_object(acro_form)
#             })
#             writer._root_object['/AcroForm'].update({
#                 NameObject('/NeedAppearances'): BooleanObject(True)
#             })

#         for page in writer.pages:
#             writer.update_page_form_field_values(page, field_mapping)

#         with open(output_pdf, 'wb') as f:
#             writer.write(f)

#         with open(output_pdf, 'rb') as f:
#             response = HttpResponse(f.read(), content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
#             return response

#     except Exception as e:
#         print("Error:", str(e))
#         return HttpResponse(f"Error: {str(e)}", status=500)





# @csrf_exempt
# def submit_form_api(request):
#     if request.method != 'POST':
#         return HttpResponse("Invalid request method", status=400)

#     try:
#         data = json.loads(request.body)
        
#         print("Received data:", data)
        
#         generate_notation_res = generate_notation(data)
#         print("Generated notation:", generate_notation_res)
#         # Save the summary to a file or database as needed
        
#         return HttpResponse(json.dumps({"notation": generate_notation_res}), content_type='application/json')
#     except json.JSONDecodeError:
#         return HttpResponse(json.dumps({"error": "Invalid JSON data"}), content_type='application/json', status=400)
    
    
    
    

    
    
    
    
@csrf_exempt
def submit_form_api(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    try:
        data = json.loads(request.body)
        
        print("Received data:", data)
        
        generate_ai_form = generate_full_va_form(data)
        print("Generated form:", generate_ai_form)
        # Save the summary to a file or database as needed
        
        return HttpResponse(json.dumps({"summary": generate_ai_form}), content_type='application/json')
    except json.JSONDecodeError:
        return HttpResponse(json.dumps({"error": "Invalid JSON data"}), content_type='application/json', status=400)
    
    
    
    
    
    

