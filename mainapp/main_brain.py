import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from mainapp.template import FORM_TEMPLATES

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUMMARY_API_KEY"))

import base64
import json
import re
import os


# # Obfuscated prompt fragments (base64 + hex + reversed)
# _p_single = b'WW91IGFyZSBhIFZBIHBvcm0gcHJvY2Vzc2luZyBleHBlcnQuIEFjY3VyYXRlbHkgcG9wdWxhdGUgdGhlIFZBIHBvcm0gdGVtcGxhdGUgZm9yIHtmb3JtX25hbWV9IHVzaW5nIHRoZSBwcm92aWRlZCBkYXRhLg=='
# _p_all = b'WW91IGFyZSBhIFZBIHBvcm0gcHJvY2Vzc2luZyBleHBlcnQuIEFjY3VyYXRlbHkgcG9wdWxhdGUgYWxsIGF2YWlsYWJsZSBWQSBmb3JtIHRlbXBsYXRlcyB1c2luZyB0aGUgcHJvdmlkZWQgZGF0YS4gVGhlIHRlbXBsYXRlcyBpbmNsdWRlOiB7dGVtcGxhdGVzX2xpc3R9Lg=='
# _p_structure = b'TWFpbnRhaW4gdGhlIG9yaWdpbmFsIEpTT04gc3RydUNCdXJlIGFuZCBhbGwga2V5cyBmcm9tIHRoZSB0ZW1wbGF0ZS4='
# _p_replace = b'UmVwbGFjZSAiTm8gVmFsdWUiIHdpdGggYXBwcm9wcmlhdGUgdmFsdWVzIGZyb20gdGhlIGlucHV0IGRhdGEgd2hlcmUgYXZhaWxhYmxlLg=='

# _p_retain = b'SWYgbm8gZGF0YSBpcyBwcm92aWRlZCBmb3IgYSBmaWVsZCwgcmV0YWluICJObyBWYWx1ZSIgb3IgaW5mZXIgcmVhc29uYWJsZSBkZWZhdWx0cyBjb21wbGlhbnQgd2l0aCBWQSBmb3JtIHJlcXVpcmVtZW50cy4='


# _p_combine = base64.b64decode(
#     'Q29tYmluZSByZWxhdGVkIGZpZWxkcyB3aGVuIGFwcHJvcHJpYXRlIChlLmcuLCBTU04gcGFydHMgaW50byBhIGZ1bGwgU1NOKS4='.encode('ascii')
# ).decode('utf-8')


# _p_invent = base64.b64decode(
#     'RG8gbm90IGludmVudCBkYXRhIHVubGVzcyBleHBsaWNpdGx5IHByb3ZpZGVkIGluIHRoZSBpbnB1dC4='.encode('ascii')
# ).decode('utf-8')[::-1]



# CONFIG = [
#     [b'Rm9sbG93IHRoZXNlIHN0ZXBzOg==', 19],  # Follow these steps:
#     [b'MS4gTWFpbnRhaW4gc3RydWN0dXJl', 0],    # 1. Maintain structure
#     [b'Mi4gUmVwbGFjZSB2YWx1ZXM=', 1],        # 2. Replace values
#     [b'My4gQ29tYmluZSBmaWVsZHM=', 2],        # 3. Combine fields
#     [b'NC4gUmV0YWluL2luZmVyIGRlZmF1bHRz', 3],# 4. Retain/infer defaults
#     [b'NS4gTm8gaW52ZW50ZWQgZGF0YQ==', 4]     # 5. No invented data
# ]

# def _d(d):
#     return base64.b64decode(d).decode('utf-8')

# def _build_instruction(form_name, templates_list):
#     parts = []
#     if form_name:
#         parts.append(_d(_p_single).format(form_name=form_name))
#     else:
#         parts.append(_d(_p_all).format(templates_list=templates_list))
    
#     # Add standard instructions
#     parts.extend([
#         _d(_p_structure),
#         _d(_p_replace),
#         _p_combine,
#         _d(_p_retain),
#         _p_invent[::-1],
#         '\n'.join([_d(c[0]) for c in CONFIG[1:]])
#     ])
    
#     # Add randomized padding
#     noise = bytes([95 ^ ord(c) for c in "SecureData"]).decode('latin-1')
#     return f"{noise}<|INSTRUCT|>{''.join(parts)}<|END|>{noise[::-1]}"

# def get_form_template(form_name):
#     # Assume FORM_TEMPLATES is defined elsewhere

#     if form_name:
#         return FORM_TEMPLATES.get(form_name, {})
#     return FORM_TEMPLATES

# def generate_full_va_form(form_data):
#     try:
#         form_name = form_data.get("pdf", "")
#         form_template = get_form_template(form_name)
        
#         if not form_template and form_name:
#             return {"error": f"No template found for {form_name}"}
        
#         templates_list = ', '.join(get_form_template("").keys()) if not form_name else ""
#         full_prompt = _build_instruction(form_name, templates_list)
#         system_msg = full_prompt.split('<|INSTRUCT|>')[1].split('<|END|>')[0]
        
#         user_input = f"Input Data:\n{json.dumps(form_data, indent=2)}"
        
#         response = client.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": system_msg},
#                 {"role": "user", "content": user_input}
#             ],
#             temperature=0.1,
#             response_format={"type": "json_object"}
#         )
        
#         content = response.choices[0].message.content
#         if content is None:
#             raise ValueError("Response content is None")
#         return json.loads(content)
    
#     except Exception as e:
#         return {"error": str(e)}
    

def validate_response(response, template):
    """Validate response against template, returning filled data and missing keys."""
    result_filled = {}
    key_missing = []

    if isinstance(template, dict) and isinstance(response, dict):
        template_keys = set(template.keys())

        # Fill fields and identify missing ones
        for key in template_keys:
            if key in response:
                result_filled[key] = response[key]
            else:
                result_filled[key] = template[key]  # Retain default "No Value"
                key_missing.append(key)

    return {
        "result_filled": result_filled,
        "key_missing": key_missing
    }


def preprocess_form_data(form_data):
    """Remove only the access_token and return the data as JSON."""
    try:
        # Create a copy to avoid modifying the original
        processed_data = form_data.copy()

        # Remove the access_token
        processed_data.pop("access_token", None)
        processed_data.pop("refresh_token", None)

        return processed_data

    except Exception as e:
        return {"error": f"Preprocessing failed: {str(e)}"}


def generate_full_va_form(form_data):
    # print("Generating VA form with data:", form_data)  # Debugging line
    processed_data = preprocess_form_data(form_data)
    print(f"Processed data for OpenAI: \n {processed_data} \n")  # Debugging line
    try:

        prompt = f"""
            Template Field Names (for reference, do not alter):
            {json.dumps({k: list(v.keys()) for k, v in FORM_TEMPLATES.items()}, indent=2)}

            User Inputed Data:
            {processed_data}
"""



        system_prompt ="""
You are an AI assistant tasked with filling out veteran affairs forms based on provided input data. The input data is structured as a dictionary with sections such as `'veteran_information'`, `'issues'`, `'conditionDetails'`, `'toxinExposure'`, `'agentOrangeLocations'`, `'gulfWarLocations'`, `'migraine'`, `'sinusitis_form'`, and others. Your goal is to map the values from these sections to the appropriate fields in the specified VA forms (e.g., `vba-21-0781-are.pdf`, `vba-21-4138-are.pdf`, `VBA-21-526EZ-ARE.pdf`, `VBA-21-0966-ARE.pdf`) accurately and comprehensively, ensuring that as many fields as possible are filled with relevant data from the input, reducing the occurrence of "No Value" entries. Follow these steps for each form:

 1: Identify the Form Type
- Recognize the specific VA form being filled (e.g., `21-526EZ` for disability compensation, `21-0781` for PTSD, `21-4138` for statements in support of claim, `21-0966` for intent to file).
- Tailor the mapping process based on the form’s purpose and field requirements.

 2: Determine Relevant Input Sections
- Match input data sections to the form’s context. Use the following guidelines:
  - **Personal Information** (all forms): Use `'veteran_information'` for fields like name, address, date of birth, phone number, email, etc.
  - **Disability Claims** (e.g., `21-526EZ`): Use `'issues'`, `'conditionDetails'`, `'migraine'`, `'sinusitis_form'` for disability names, descriptions, start dates, and treatment details.
  - **Exposure Information** (e.g., `21-526EZ`, `21-0781`): Use `'toxinExposure'`, `'agentOrangeLocations'`, `'gulfWarLocations'` for exposure types, locations, and dates.
  - **Medical Conditions** (e.g., `21-526EZ`): Use `'migraine'`, `'sinusitis_form'` for symptoms, frequency, and treatment history.
  - **Service Details** (e.g., `21-526EZ`): Use `'veteran_information'` for service dates, branch, and location.
  - **General Remarks** (e.g., `21-4138`): Summarize relevant details from multiple sections if specific fields are unavailable.

 3: Map Input Values to Form Fields
- For each field in the form:
  - **Direct Mapping**: Search the input data for an exact or near-exact match based on key names or context. Examples:
    - `'Veterans_Beneficiary_First_Name'` → `Veterans_Service_Members_First_Name[0]` or `Veterans_First_Name[0]`
    - `'Last_Name'` → `VeteransLastName[0]` or `Veteran_Service_Member_Last_Name[0]`
    - `'DOB_Month'`, `'DOB_Day'`, `'DOB_Year'` → Combine into `Date_Of_Birth_Month[0]`, `Date_Of_Birth_Day[0]`, `Date_Of_Birth_Year[0]`
    - `'CURRENTDISABILITY'` → `CURRENTDISABILITY[0]`, `CURRENTDISABILITY[1]`, etc., for multiple entries
    - `'agentOrangeLocations'` → `List_Other_Locations_Where_You_Served[0]` or exposure-related fields
  - **Semantic Mapping**: If no direct match exists, infer the field based on meaning:
    - `'migraineFrequency'` and `'migraineSymptoms'` → Fields like `ExplainHowDisabilityRelatesToEvent_Exposure_Injury[0]`
    - `'toxinExposure'` (e.g., `ASBESTOS: [True]`) → `ASBESTOS[0]` or related exposure checkboxes
  - **Multiple Instances**: Handle fields with indices (e.g., `[0]`, `[1]`) by mapping list items from the input sequentially.

 4: Infer Values When Necessary
- If a direct match isn’t available but related data exists:
  - Combine related fields (e.g., `'Beginning_Date_Month'`, `'Beginning_Date_Day'`, `'Beginning_Date_Year'` into a full date for `From_Date_Month[0]`, etc.).
  - Use context to fill narrative fields (e.g., `'details'` from `'sinusitis_form'` or `'migraine'` into `REMARKS[0]` or `Additional_Details`).
  - For yes/no fields, interpret input values like `'YES'` or `True` as "Selected" and `'NO'` or `False` as unselected.

 5: Handle Missing Data
- If no matching or inferable data exists for a field:
  - Set it to `"No Value"`.
  - Optionally, append a note in a remarks field (e.g., `REMARKS[2]`) stating, "Additional information may be required for [field name]."

 6: Format and Validate Output
- Ensure values match the field’s expected format (e.g., dates as `MM/DD/YYYY`, checkboxes as `"Selected"` or unselected).
- Preserve the output structure (form names with nested field-value pairs) as shown in the provided example.
- Handle multiple instances of fields (e.g., multiple exposure locations or disabilities) by incrementing indices appropriately.

Additional Instructions
- **Maximize Data Usage**: Exhaustively search all input sections to avoid missing relevant data. For example, use `'veteran_information'` for address fields across all forms, not just remarks.
- **Avoid Overgeneralization**: Do not fill fields with generic summaries unless explicitly mapped; prefer specific mappings where possible.
- **Consistency**: Apply the same mapping logic across all forms for shared fields (e.g., name, SSN, address).

Output
- Return the filled form data in a JSON-like structure, with each form name as a key and its fields as nested key-value pairs, mirroring the provided output format.

Your primary objective is to reduce "No Value" entries by accurately and intelligently mapping the input data to the form fields, using both direct matches and reasonable inferences based on the context of each form."""


        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.1,
            # max_tokens=4096
        )

        # Sanitize and parse response
        raw_response = response.choices[0].message.content.strip()

        print(f"Raw OpenAI response: {raw_response}")  # Debugging line

        # Use regex to extract JSON content between ```json and ```
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_response, re.MULTILINE)
        if json_match:
            raw_response = json_match.group(1).strip()
        else:
            # Fallback: Remove any leading/trailing backticks or preamble
            raw_response = raw_response.strip('```').strip()
            if raw_response.startswith('Below is the formatted output'):
                raw_response = raw_response.split('```json', 1)[-1].strip('```').strip()

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError as e:
            return {
                "result_filled": {},
                "key_missing": {},
                "error": f"Failed to parse OpenAI response: {str(e)}. Raw response: {raw_response[:500]}..."
            }