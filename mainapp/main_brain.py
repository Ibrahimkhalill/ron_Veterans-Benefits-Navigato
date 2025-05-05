import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from mainapp.template import FORM_TEMPLATES

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUMMARY_API_KEY"))

import base64
import json


# Obfuscated prompt fragments (base64 + hex + reversed)
_p_single = b'WW91IGFyZSBhIFZBIHBvcm0gcHJvY2Vzc2luZyBleHBlcnQuIEFjY3VyYXRlbHkgcG9wdWxhdGUgdGhlIFZBIHBvcm0gdGVtcGxhdGUgZm9yIHtmb3JtX25hbWV9IHVzaW5nIHRoZSBwcm92aWRlZCBkYXRhLg=='
_p_all = b'WW91IGFyZSBhIFZBIHBvcm0gcHJvY2Vzc2luZyBleHBlcnQuIEFjY3VyYXRlbHkgcG9wdWxhdGUgYWxsIGF2YWlsYWJsZSBWQSBmb3JtIHRlbXBsYXRlcyB1c2luZyB0aGUgcHJvdmlkZWQgZGF0YS4gVGhlIHRlbXBsYXRlcyBpbmNsdWRlOiB7dGVtcGxhdGVzX2xpc3R9Lg=='
_p_structure = b'TWFpbnRhaW4gdGhlIG9yaWdpbmFsIEpTT04gc3RydUNCdXJlIGFuZCBhbGwga2V5cyBmcm9tIHRoZSB0ZW1wbGF0ZS4='
_p_replace = b'UmVwbGFjZSAiTm8gVmFsdWUiIHdpdGggYXBwcm9wcmlhdGUgdmFsdWVzIGZyb20gdGhlIGlucHV0IGRhdGEgd2hlcmUgYXZhaWxhYmxlLg=='

_p_retain = b'SWYgbm8gZGF0YSBpcyBwcm92aWRlZCBmb3IgYSBmaWVsZCwgcmV0YWluICJObyBWYWx1ZSIgb3IgaW5mZXIgcmVhc29uYWJsZSBkZWZhdWx0cyBjb21wbGlhbnQgd2l0aCBWQSBmb3JtIHJlcXVpcmVtZW50cy4='


_p_combine = base64.b64decode(
    'Q29tYmluZSByZWxhdGVkIGZpZWxkcyB3aGVuIGFwcHJvcHJpYXRlIChlLmcuLCBTU04gcGFydHMgaW50byBhIGZ1bGwgU1NOKS4='.encode('ascii')
).decode('utf-8')


_p_invent = base64.b64decode(
    'RG8gbm90IGludmVudCBkYXRhIHVubGVzcyBleHBsaWNpdGx5IHByb3ZpZGVkIGluIHRoZSBpbnB1dC4='.encode('ascii')
).decode('utf-8')[::-1]



CONFIG = [
    [b'Rm9sbG93IHRoZXNlIHN0ZXBzOg==', 19],  # Follow these steps:
    [b'MS4gTWFpbnRhaW4gc3RydWN0dXJl', 0],    # 1. Maintain structure
    [b'Mi4gUmVwbGFjZSB2YWx1ZXM=', 1],        # 2. Replace values
    [b'My4gQ29tYmluZSBmaWVsZHM=', 2],        # 3. Combine fields
    [b'NC4gUmV0YWluL2luZmVyIGRlZmF1bHRz', 3],# 4. Retain/infer defaults
    [b'NS4gTm8gaW52ZW50ZWQgZGF0YQ==', 4]     # 5. No invented data
]

def _d(d):
    return base64.b64decode(d).decode('utf-8')

def _build_instruction(form_name, templates_list):
    parts = []
    if form_name:
        parts.append(_d(_p_single).format(form_name=form_name))
    else:
        parts.append(_d(_p_all).format(templates_list=templates_list))
    
    # Add standard instructions
    parts.extend([
        _d(_p_structure),
        _d(_p_replace),
        _p_combine,
        _d(_p_retain),
        _p_invent[::-1],
        '\n'.join([_d(c[0]) for c in CONFIG[1:]])
    ])
    
    # Add randomized padding
    noise = bytes([95 ^ ord(c) for c in "SecureData"]).decode('latin-1')
    return f"{noise}<|INSTRUCT|>{''.join(parts)}<|END|>{noise[::-1]}"

def get_form_template(form_name):
    # Assume FORM_TEMPLATES is defined elsewhere

    if form_name:
        return FORM_TEMPLATES.get(form_name, {})
    return FORM_TEMPLATES

def generate_full_va_form(form_data):
    try:
        form_name = form_data.get("pdf", "")
        form_template = get_form_template(form_name)
        
        if not form_template and form_name:
            return {"error": f"No template found for {form_name}"}
        
        templates_list = ', '.join(get_form_template("").keys()) if not form_name else ""
        full_prompt = _build_instruction(form_name, templates_list)
        system_msg = full_prompt.split('<|INSTRUCT|>')[1].split('<|END|>')[0]
        
        user_input = f"Input Data:\n{json.dumps(form_data, indent=2)}"
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Response content is None")
        return json.loads(content)
    
    except Exception as e:
        return {"error": str(e)}
    
    
    
    
