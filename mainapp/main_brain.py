import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from mainapp.template import FORM_TEMPLATES

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUMMARY_API_KEY"))

import base64
import json


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
            The templates include: {', '.join(FORM_TEMPLATES.keys())}. 
            Replace "No Value" with values from the input data where available. 
            Combine related fields when appropriate (e.g., SSN parts into a full SSN, but preserve individual SSN fields if specified in the template). 
            If no data is provided for a field, retain a generated value or infer reasonable defaults where applicable, ensuring compliance with VA form requirements.
            Do not invent data unless explicitly provided in the input. Do not modify, normalize, or change the case of field names (e.g., 'VeteransLastName' must remain 'VeteransLastName', not 'veteran_last_name').
            
            focusing on creating detailed, VA-compliant notations for the REMARKS fields (REMARKS[0], REMARKS[1]). Follow these instructions precisely:

            1. **REMARKS Fields**:
            - **REMARKS[0]**: Summarize the veteran's medical conditions (e.g., migraines, tinnitus, sinusitis) using data from 'migraine', 'tinnitus_hearing_loss', 'sinusitis_form', and 'conditionDetails'. Include details on onset (e.g., StartDate), symptoms, frequency, impact, and any relevant medical history. Ensure the notation is concise, professional, and compliant with VA form requirements.
            - **REMARKS[1]**: Summarize service-related exposures using data from 'toxinExposure', 'agentOrangeLocations', and 'gulfWarLocations'. Describe potential links to the veteran's conditions, including specific toxins (e.g., mustard gas, contaminated water), locations, and exposure events. Ensure the notation is detailed and VA-compliant.

            2. **Non-REMARKS Fields (#subform[0], #subform[1], form1[0])**:
            - If the field is directly provided in the input data and matches the template exactly, use that value.
            - If no data is provided, generate a reasonable default:
                - For name-related fields, use a generic name like "John Doe".
                - For other fields (e.g., #subform[0], #subform[1], form1[0]), use "N/A" to indicate not applicable or unavailable.

            
            # Use relevant input data (example: 'migraine.details', 'tinnitus_hearing_loss.details', 'sinusitis_form.details', 'conditionDetails.ExplainHowDisabilityRelatesToEvent_Exposure_Injury') to create comprehensive notations for REMARKS[0] and REMARKS[1]. 
            # For REMARKS[0], focus on summarizing conditions like migraines, tinnitus, and sinusitis, including onset, symptoms, and impact. 
            # For REMARKS[1], detail service-related exposures (example: toxinExposure, agentOrangeLocations, gulfWarLocations) and their potential link to the conditions.  

            Template Field Names (for reference, do not alter):
            {json.dumps({k: list(v.keys()) for k, v in FORM_TEMPLATES.items()}, indent=2)}

            Input Data:
            {processed_data}

            Return a JSON object where each key is a form name (e.g., 'vba-21-4138-are.pdf') and the value is the completed JSON with the EXACT structure and field names of that form's template:"""

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a VA form processing expert. Strictly follow the template structure and VA form requirements, preserving EXACT field names."},
                {"role": "user", "content": prompt}
            ],
            # temperature=0.1,
            # max_tokens=4096
        )

        # Sanitize and parse response
        raw_response = response.choices[0].message.content.strip()
        print(f"Raw OpenAI response: {raw_response}")  # Debugging line
        
        if raw_response.startswith("```json"):
            raw_response = raw_response[7:-3].strip()
        elif raw_response.startswith("```"):
            raw_response = raw_response.strip()

        try:
            result = json.loads(raw_response)
        except json.JSONDecodeError as e:
            return {
                "result_filled": {},
                "key_missing": {},
                "error": f"Failed to parse OpenAI response: {str(e)}. Raw response: {raw_response[:500]}..."
            }

        # Initialize output dictionaries
        output = {
            "result_filled": {},
            "key_missing": {}
        }

        # Validate response
        # if form_name:
        #     validation_result = validate_response(result, form_template, form_name)
        #     output["result_filled"] = validation_result["result_filled"]
        #     output["key_missing"] = {form_name: validation_result["key_missing"]}
        # else:
        if isinstance(result, dict):
            for fname in FORM_TEMPLATES.keys():
                if fname in result:
                    validation_result = validate_response(result[fname], FORM_TEMPLATES[fname])
                    output["result_filled"][fname] = validation_result["result_filled"]
                    output["key_missing"][fname] = validation_result["key_missing"]
                else:
                    output["key_missing"][fname] = list(FORM_TEMPLATES[fname].keys())
                    output["result_filled"][fname] = FORM_TEMPLATES[fname].copy()

        return output

    except Exception as e:
        return {
            "result_filled": {},
            "key_missing": {},
            "error": f"Unexpected error: {str(e)}"
        }
