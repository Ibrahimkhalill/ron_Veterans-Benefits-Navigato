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
             {"role": "system", "content": "You are a summarizer assistant that only summarizes VA forms and Write a VA narration for a veteran"},
            {"role": "user", "content": prompt}
        ],
        )
        # Extract and return the assistant's response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"




def generate_pdf(data):
    try:
        pdf_files = {
            'VBA-21-526EZ-ARE.pdf': 'VBA-21-526EZ-ARE.pdf',
            'vba-21-0781-are.pdf': 'vba-21-0781-are.pdf',
            'vba-21-4138-are.pdf': 'vba-21-4138-are.pdf',
            'VBA-21-0966-ARE.pdf': 'VBA-21-0966-ARE.pdf'
        }

        # Use VA File Number as identifier since SSN is empty
        ssn = data.get('VBA-21-526EZ-ARE.pdf', {}).get('VA_File_Number[0]', '123456789')

        generated_pdfs = []

        for pdf_name, data_key in pdf_files.items():
            field_mapping = data.get(data_key, {})
            if not field_mapping and pdf_name == 'VBA-21-0966-ARE.pdf':
                print(f"Skipping {pdf_name}: No data provided")
                continue

            input_pdf = os.path.join(settings.STATICFILES_DIRS[0], 'pdfs', pdf_name)
            output_filename = f'filled_{ssn}_{pdf_name}'
            output_pdf = os.path.join(settings.MEDIA_ROOT, output_filename)

            if not os.path.exists(input_pdf):
                print(f"Error: Input PDF {pdf_name} not found")
                continue

            reader = PdfReader(input_pdf)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            if '/AcroForm' in reader.trailer['/Root']:
                acro_form = reader.trailer['/Root']['/AcroForm']
                writer._root_object.update({
                    NameObject('/AcroForm'): writer._add_object(acro_form)
                })
                writer._root_object['/AcroForm'].update({
                    NameObject('/NeedAppearances'): BooleanObject(True)
                })

            for page in writer.pages:
                writer.update_page_form_field_values(page, field_mapping)

            with open(output_pdf, 'wb') as f:
                writer.write(f)

            generated_pdfs.append((output_filename, output_pdf))

        if not generated_pdfs:
            return HttpResponse("Error: No PDFs generated", status=500)

        # Return the first PDF for testing
        output_filename, output_pdf = generated_pdfs[0]
        with open(output_pdf, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
        return response

    except Exception as e:
        print("Error:", str(e))
        return HttpResponse(f"Error: {str(e)}", status=500)





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
    
    
    
    
dummy_form_data= {
  "agentOrangeLocations": {
    "locations": ["Vietnam", "Thailand (U-Tapao Air Base, Nakhon Phanom)"]
  },
  "migraine": {
    "migraineFrequency": "3-4 times per month",
    "migraineDuration": "2-6 hours",
    "migraineSymptoms": "Throbbing pain, nausea, sensitivity to light and sound",
    "migraineImpact": "Inability to work or perform tasks during episodes",
    "medicalVisitDates": "2025-03-15, 2025-04-10",
    "details": "Episodes have increased in frequency since deployment"
  },
  "verified_email": "dummy.veteran@example.com",
  "issues": {
    "CURRENTDISABILITY": ["Prostrating Migraines", "Chronic Sinusitis"]
  },
  "gulfWarLocations": {
    "List_Other_Locations_Where_You_Served": ["Iraq", "Saudi Arabia", "Kuwait"]
  },
  "toxinExposure": {
    "ASBESTOS": [True],
    "SHAD_Shipboard_Hazard_And_Defense": [False],
    "Mustard_Gas": [True],
    "Military_Occupational_Specialty_MOS_Related_Toxin": [True],
    "Radiation": True,
    "Contaminated_Water_At_Camp_Lejeune": [True],
    "Jet_Fuel": True,
    "Other_Toxins": "Burn pit smoke, diesel exhaust",
    "Additional_Details": "Heavy exposure during field ops and airfield duty",
    "OTHER_Specify": ["Lead-based paint", "Solvents", "NO"],
    "Provide_Additional_Dates_And_Locations_Of_Potential_Exposure": [
      "2020-04 to 2020-11 – Burn pit exposure near Camp Buehring, Kuwait",
      "2018-06 to 2018-09 – Radiation exposure while stationed at radar base"
    ]
  },
  "sinusitis_form": {
    "runnyNose": "YES",
    "complainedWhileInService": "YES",
    "exposedToBurnPits": "YES",
    "symptomsStartDate": "2019-11-01",
    "symptomsFrequency": "DAILY",
    "dailyMedication": "YES",
    "officiallyDiagnosed": "YES",
    "treatmentProvided": "YES",
    "details": "Chronic sinus congestion and facial pressure, worsens with dust"
  },
  "veteran_information": {
    "Beginning_Date_Month": ["01"],
    "Beginning_Date_Day": ["15"],
    "Beginning_Date_Year": ["2005"],
    "Ending_Date_Month": ["12"],
    "Ending_Date_Day": ["20"],
    "Ending_Date_Year": ["2024"],
    "Veterans_Beneficiary_First_Name": ["Md."],
    "Last_Name": ["Ibrahim"],
    "EMAIL_ADDRESS": ["dummy.veteran@example.com", "ibrahimalt@example.com"],
    "International_Phone_Number": ["+8801555555555"],
    "TelephoneNumber_FirstThreeNumbers": ["321"],
    "TelephoneNumber_SecondThreeNumbers": ["654"],
    "TelephoneNumber_LastFourNumbers": ["7890"],
    "DOB_Month": ["12"],
    "DOB_Day": ["10"],
    "DOB_Year": ["1990"],
    "MailingAddress_NumberAndStreet": ["1234 Freedom Blvd"],
    "MailingAddress_ApartmentOrUnitNumber": ["12B"],
    "MailingAddress_City": ["San Diego"],
    "MailingAddress_StateOrProvince": ["CA"],
    "MailingAddress_Country": ["US"],
    "MailingAddress_ZIPOrPostalCode_FirstFiveNumbers": ["92101"],
    "MailingAddress_ZIPOrPostalCode_LastFourNumbers": ["1234"],
    "branchOfService": "Marine Corps",
    "serviceUnder": "Yes",
    "placeOfService": "Camp Pendleton",
    "nationalGuardReserves": "No",
    "guardReservesDates": "",
    "activeDutyOrders": "Yes",
    "vaDirectDeposit": "Yes",
    "vaHealthCare": "Yes",
    "livingSituation": "Living Alone"
  },
  "otp": "123456",
  "conditionDetails": {
    "Specify_Type_Of_Exposure_Event_Or_Injury": ["Prostrating Migraines", "Chronic Sinusitis"],
    "ExplainHowDisabilityRelatesToEvent_Exposure_Injury": [
      "Exposure to intense heat and jet fuel fumes triggered migraine episodes",
      "Continuous exposure to burn pits and desert dust caused chronic sinus inflammation"
    ],
    "StartDate": ["2020-06-10", "2019-11-01"],
    "Location": [
      {"left": False, "right": False, "both": True},
      {"left": False, "right": False, "both": True}
    ]
  },
  "document": {
    "discharge_condition": {
      "type": "Honorable",
      "date": "2024-12-20"
    },
    "evidenceData": {
      "uploadedMedicalRecords": True,
      "supportingBuddyStatements": True,
      "serviceTreatmentRecords": True
    }
  }
}

    
    
    
    
@csrf_exempt
def submit_form_api(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    try:
        data = json.loads(request.body)
        # print("Received data:", data)
        
        # dummy_data = json.dumps(dummy_form_data)
        # print("Dummy data:", dummy_data)
        
        # Simulate request.body as bytes
        request_body_sim = json.dumps(dummy_form_data).encode('utf-8')

        # Emulate receiving and decoding the request
        data = json.loads(request_body_sim)
        # print("Received data:", data)
        
        # print("Received data:", data)
        
        generate_ai_form = generate_full_va_form(data)
        # print("Generated form:", generate_ai_form)
        print("result", generate_ai_form["result_filled"])
       
        generate_pdf(generate_ai_form["result_filled"])
        
        
        
        
        # Save the summary to a file or database as needed
        
        summery = generate_notation(data) 
        
               
        return HttpResponse(json.dumps({"notation": summery, "AI_filled_VA_PDF_Fields": generate_ai_form}), content_type='application/json')
    except json.JSONDecodeError:
        return HttpResponse(json.dumps({"error": "Invalid JSON data"}), content_type='application/json', status=400)
    
    
    
    
    
    

