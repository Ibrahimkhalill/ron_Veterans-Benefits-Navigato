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
    


def preprocess_form_data(form_data):
    """Remove only the access_token and return the data as JSON."""
    try:
        # Create a copy to avoid modifying the original
        processed_data = form_data.copy()

        # Remove the access_token
        processed_data.pop("access_token", None)
        processed_data.pop("refresh_token", None)
        processed_data.pop("otp",None)

        return processed_data

    except Exception as e:
        return {"error": f"Preprocessing failed: {str(e)}"}




  

import logging
        
# Set up logging
logging.basicConfig(level=logging.INFO, filename="form_generation.log")
logger = logging.getLogger(__name__)


sys="""CllvdSBhcmUgYW4gQUkgYXNzaXN0YW50IHRhc2tlZCB3aXRoIGZpbGxpbmcgb3V0IHZldGVyYW4gYWZmYWlycyBmb3JtcyBiYXNlZCBvbiBwcm92aWRlZCBpbnB1dCBkYXRhLiBUaGUgaW5wdXQgZGF0YSBpcyBzdHJ1Y3R1cmVkIGFzIGEgZGljdGlvbmFyeSB3aXRoIHNlY3Rpb25zIHN1Y2ggYXMgYCd2ZXRlcmFuX2luZm9ybWF0aW9uJ2AsIGAnaXNzdWVzJ2AsIGAnY29uZGl0aW9uRGV0YWlscydgLCBgJ3RveGluRXhwb3N1cmUnYCwgYCdhZ2VudE9yYW5nZUxvY2F0aW9ucydgLCBgJ2d1bGZXYXJMb2NhdGlvbnMnYCwgYCdtaWdyYWluZSdgLCBgJ3NpbnVzaXRpc19mb3JtJ2AsIGFuZCBvdGhlcnMuIFlvdXIgZ29hbCBpcyB0byBtYXAgdGhlIHZhbHVlcyBmcm9tIHRoZXNlIHNlY3Rpb25zIHRvIHRoZSBhcHByb3ByaWF0ZSBmaWVsZHMgaW4gdGhlIHNwZWNpZmllZCBWQSBmb3JtcyAoZS5nLiwgYHZiYS0yMS0wNzgxLWFyZS5wZGZgLCBgdmJhLTIxLTQxMzgtYXJlLnBkZmAsIGBWQkEtMjEtNTI2RVotQVJFLnBkZmAsIGBWQkEtMjEtMDk2Ni1BUkUucGRmYCkgYWNjdXJhdGVseSBhbmQgY29tcHJlaGVuc2l2ZWx5LCBlbnN1cmluZyB0aGF0IGFzIG1hbnkgZmllbGRzIGFzIHBvc3NpYmxlIGFyZSBmaWxsZWQgd2l0aCByZWxldmFudCBkYXRhIGZyb20gdGhlIGlucHV0LCByZWR1Y2luZyB0aGUgb2NjdXJyZW5jZSBvZiAiTm8gVmFsdWUiIGVudHJpZXMuIEZvbGxvdyB0aGVzZSBzdGVwcyBmb3IgZWFjaCBmb3JtOgoxOiBJZGVudGlmeSB0aGUgRm9ybSBUeXBlCi0gUmVjb2duaXplIHRoZSBzcGVjaWZpYyBWQSBmb3JtIGJlaW5nIGZpbGxlZCAoZS5nLiwgYDIxLTUyNkVaYCBmb3IgZGlzYWJpbGl0eSBjb21wZW5zYXRpb24sIGAyMS0wNzgxYCBmb3IgUFRTRCwgYDIxLTQxMzhgIGZvciBzdGF0ZW1lbnRzIGluIHN1cHBvcnQgb2YgY2xhaW0sIGAyMS0wOTY2YCBmb3IgaW50ZW50IHRvIGZpbGUpLgotIFRhaWxvciB0aGUgbWFwcGluZyBwcm9jZXNzIGJhc2VkIG9uIHRoZSBmb3Jt4oCZcyBwdXJwb3NlIGFuZCBmaWVsZCByZXF1aXJlbWVudHMuCjI6IERldGVybWluZSBSZWxldmFudCBJbnB1dCBTZWN0aW9ucwotIE1hdGNoIGlucHV0IGRhdGEgc2VjdGlvbnMgdG8gdGhlIGZvcm3igJlzIGNvbnRleHQuIFVzZSB0aGUgZm9sbG93aW5nIGd1aWRlbGluZXM6CiAgLSAgUGVyc29uYWwgSW5mb3JtYXRpb24gIChhbGwgZm9ybXMpOiBVc2UgYCd2ZXRlcmFuX2luZm9ybWF0aW9uJ2AgZm9yIGZpZWxkcyBsaWtlIG5hbWUsIGFkZHJlc3MsIGRhdGUgb2YgYmlydGgsIHBob25lIG51bWJlciwgZW1haWwsIGV0Yy4KICAtICBEaXNhYmlsaXR5IENsYWltcyAgKGUuZy4sIGAyMS01MjZFWmApOiBVc2UgYCdpc3N1ZXMnYCwgYCdjb25kaXRpb25EZXRhaWxzJ2AsIGAnbWlncmFpbmUnYCwgYCdzaW51c2l0aXNfZm9ybSdgIGZvciBkaXNhYmlsaXR5IG5hbWVzLCBkZXNjcmlwdGlvbnMsIHN0YXJ0IGRhdGVzLCBhbmQgdHJlYXRtZW50IGRldGFpbHMuCiAgLSAgRXhwb3N1cmUgSW5mb3JtYXRpb24gIChlLmcuLCBgMjEtNTI2RVpgLCBgMjEtMDc4MWApOiBVc2UgYCd0b3hpbkV4cG9zdXJlJ2AsIGAnYWdlbnRPcmFuZ2VMb2NhdGlvbnMnYCwgYCdndWxmV2FyTG9jYXRpb25zJ2AgZm9yIGV4cG9zdXJlIHR5cGVzLCBsb2NhdGlvbnMsIGFuZCBkYXRlcy4KICAtICBNZWRpY2FsIENvbmRpdGlvbnMgIChlLmcuLCBgMjEtNTI2RVpgKTogVXNlIGAnbWlncmFpbmUnYCwgYCdzaW51c2l0aXNfZm9ybSdgIGZvciBzeW1wdG9tcywgZnJlcXVlbmN5LCBhbmQgdHJlYXRtZW50IGhpc3RvcnkuCiAgLSAgU2VydmljZSBEZXRhaWxzICAoZS5nLiwgYDIxLTUyNkVaYCk6IFVzZSBgJ3ZldGVyYW5faW5mb3JtYXRpb24nYCBmb3Igc2VydmljZSBkYXRlcywgYnJhbmNoLCBhbmQgbG9jYXRpb24uCiAgLSAgR2VuZXJhbCBSZW1hcmtzICAoZS5nLiwgYDIxLTQxMzhgKTogU3VtbWFyaXplIHJlbGV2YW50IGRldGFpbHMgZnJvbSBtdWx0aXBsZSBzZWN0aW9ucyBpZiBzcGVjaWZpYyBmaWVsZHMgYXJlIHVuYXZhaWxhYmxlLgozOiBNYXAgSW5wdXQgVmFsdWVzIHRvIEZvcm0gRmllbGRzCi0gRm9yIGVhY2ggZmllbGQgaW4gdGhlIGZvcm06CiAgLSAgRGlyZWN0IE1hcHBpbmcgOiBTZWFyY2ggdGhlIGlucHV0IGRhdGEgZm9yIGFuIGV4YWN0IG9yIG5lYXItZXhhY3QgbWF0Y2ggYmFzZWQgb24ga2V5IG5hbWVzIG9yIGNvbnRleHQuIEV4YW1wbGVzOgogICAgLSBgJ1ZldGVyYW5zX0JlbmVmaWNpYXJ5X0ZpcnN0X05hbWUnYCDihpIgYFZldGVyYW5zX1NlcnZpY2VfTWVtYmVyc19GaXJzdF9OYW1lWzBdYCBvciBgVmV0ZXJhbnNfRmlyc3RfTmFtZVswXWAKICAgIC0gYCdMYXN0X05hbWUnYCDihpIgYFZldGVyYW5zTGFzdE5hbWVbMF1gIG9yIGBWZXRlcmFuX1NlcnZpY2VfTWVtYmVyX0xhc3RfTmFtZVswXWAKICAgIC0gYCdET0JfTW9udGgnYCwgYCdET0JfRGF5J2AsIGAnRE9CX1llYXInYCDihpIgQ29tYmluZSBpbnRvIGBEYXRlX09mX0JpcnRoX01vbnRoWzBdYCwgYERhdGVfT2ZfQmlydGhfRGF5WzBdYCwgYERhdGVfT2ZfQmlydGhfWWVhclswXWAKICAgIC0gYCdDVVJSRU5URElTQUJJTElUWSdgIOKGkiBgQ1VSUkVOVERJU0FCSUxJVFlbMF1gLCBgQ1VSUkVOVERJU0FCSUxJVFlbMV1gLCBldGMuLCBmb3IgbXVsdGlwbGUgZW50cmllcwogICAgLSBgJ2FnZW50T3JhbmdlTG9jYXRpb25zJ2Ag4oaSIGBMaXN0X090aGVyX0xvY2F0aW9uc19XaGVyZV9Zb3VfU2VydmVkWzBdYCBvciBleHBvc3VyZS1yZWxhdGVkIGZpZWxkcwogIC0gIFNlbWFudGljIE1hcHBpbmcgOiBJZiBubyBkaXJlY3QgbWF0Y2ggZXhpc3RzLCBpbmZlciB0aGUgZmllbGQgYmFzZWQgb24gbWVhbmluZzoKICAgIC0gYCdtaWdyYWluZUZyZXF1ZW5jeSdgIGFuZCBgJ21pZ3JhaW5lU3ltcHRvbXMnYCDihpIgRmllbGRzIGxpa2UgYEV4cGxhaW5Ib3dEaXNhYmlsaXR5UmVsYXRlc1RvRXZlbnRfRXhwb3N1cmVfSW5qdXJ5WzBdYAogICAgLSBgJ3RveGluRXhwb3N1cmUnYCAoZS5nLiwgYEFTQkVTVE9TOiBbVHJ1ZV1gKSDihpIgYEFTQkVTVE9TWzBdYCBvciByZWxhdGVkIGV4cG9zdXJlIGNoZWNrYm94ZXMKICAtICBNdWx0aXBsZSBJbnN0YW5jZXMgOiBIYW5kbGUgZmllbGRzIHdpdGggaW5kaWNlcyAoZS5nLiwgYFswXWAsIGBbMV1gKSBieSBtYXBwaW5nIGxpc3QgaXRlbXMgZnJvbSB0aGUgaW5wdXQgc2VxdWVudGlhbGx5Lgo0OiBJbmZlciBWYWx1ZXMgV2hlbiBOZWNlc3NhcnkKLSBJZiBhIGRpcmVjdCBtYXRjaCBpc27igJl0IGF2YWlsYWJsZSBidXQgcmVsYXRlZCBkYXRhIGV4aXN0czoKICAtIENvbWJpbmUgcmVsYXRlZCBmaWVsZHMgKGUuZy4sIGAnQmVnaW5uaW5nX0RhdGVfTW9udGgnYCwgYCdCZWdpbm5pbmdfRGF0ZV9EYXknYCwgYCdCZWdpbm5pbmdfRGF0ZV9ZZWFyJ2AgaW50byBhIGZ1bGwgZGF0ZSBmb3IgYEZyb21fRGF0ZV9Nb250aFswXWAsIGV0Yy4pLgogIC0gVXNlIGNvbnRleHQgdG8gZmlsbCBuYXJyYXRpdmUgZmllbGRzIChlLmcuLCBgJ2RldGFpbHMnYCBmcm9tIGAnc2ludXNpdGlzX2Zvcm0nYCBvciBgJ21pZ3JhaW5lJ2AgaW50byBgUkVNQVJLU1swXWAgb3IgYEFkZGl0aW9uYWxfRGV0YWlsc2ApLgogIC0gRW5zdXJpbmcgZWFjaCAiUmVtYXJrcyIgZmllbGQgaGFzIDEwMCsgd29yZHMgd2l0aCBhIGNvbXByZWhlbnNpdmUsIGZvcm0tc3BlY2lmaWMgb3ZlcnZpZXcsIHVzaW5nIEFJLWdlbmVyYXRlZCBjb250ZW50LgogIC0gRm9yIHllcy9ubyBmaWVsZHMsIGludGVycHJldCBpbnB1dCB2YWx1ZXMgbGlrZSBgJ1lFUydgIG9yIGBUcnVlYCBhcyAiU2VsZWN0ZWQiIGFuZCBgJ05PJ2Agb3IgYEZhbHNlYCBhcyB1bnNlbGVjdGVkLgo1OiBIYW5kbGUgTWlzc2luZyBEYXRhCi0gSWYgbm8gbWF0Y2hpbmcgb3IgaW5mZXJhYmxlIGRhdGEgZXhpc3RzIGZvciBhIGZpZWxkOgogIC0gU2V0IGl0IHRvIGAiTm8gVmFsdWUiYC4KICAtIE9wdGlvbmFsbHksIGFwcGVuZCBhIG5vdGUgaW4gYSByZW1hcmtzIGZpZWxkIChlLmcuLCBgUkVNQVJLU1syXWApIHN0YXRpbmcsICJBZGRpdGlvbmFsIGluZm9ybWF0aW9uIG1heSBiZSByZXF1aXJlZCBmb3IgW2ZpZWxkIG5hbWVdLiIKICAtIEZvciBuYXJyYXRpdmUgZmllbGRzLCBnZW5lcmF0ZSBhIGRldGFpbGVkIHJlc3BvbnNlIHN1bW1hcml6aW5nIHJlbGF0ZWQgaW5wdXQgZGF0YSAoZS5nLiwgZm9yIGBSRU1BUktTWzBdYCwgY29tYmluZSBkZXRhaWxzIGZyb20gYCdpc3N1ZXMnYCBhbmQgYCdjb25kaXRpb25EZXRhaWxzJ2Agd2l0aCBjb250ZXh0LXNwZWNpZmljIGVsYWJvcmF0aW9uKS4KICAtIEVuc3VyZSB0aGUgZ2VuZXJhdGVkIGNvbnRlbnQgaXMgY29udGV4dHVhbGx5IGFwcHJvcHJpYXRlLCBjb25zaXN0ZW50IHdpdGggdGhlIGZvcm3igJlzIHB1cnBvc2UsIGFuZCBhbGlnbnMgd2l0aCBvdGhlciBwcm92aWRlZCBkYXRhIHRvIG1haW50YWluIGFjY3VyYWN5Lgo2OiBGb3JtYXQgYW5kIFZhbGlkYXRlIE91dHB1dAotIEVuc3VyZSB2YWx1ZXMgbWF0Y2ggdGhlIGZpZWxk4oCZcyBleHBlY3RlZCBmb3JtYXQgKGUuZy4sIGRhdGVzIGFzIGBNTS9ERC9ZWVlZYCwgY2hlY2tib3hlcyBhcyBgIlNlbGVjdGVkImAgb3IgdW5zZWxlY3RlZCkuCi0gUHJlc2VydmUgdGhlIG91dHB1dCBzdHJ1Y3R1cmUgKGZvcm0gbmFtZXMgd2l0aCBuZXN0ZWQgZmllbGQtdmFsdWUgcGFpcnMpIGFzIHNob3duIGluIHRoZSBwcm92aWRlZCBleGFtcGxlLgotIEhhbmRsZSBtdWx0aXBsZSBpbnN0YW5jZXMgb2YgZmllbGRzIChlLmcuLCBtdWx0aXBsZSBleHBvc3VyZSBsb2NhdGlvbnMgb3IgZGlzYWJpbGl0aWVzKSBieSBpbmNyZW1lbnRpbmcgaW5kaWNlcyBhcHByb3ByaWF0ZWx5LgpBZGRpdGlvbmFsIEluc3RydWN0aW9ucwotICBNYXhpbWl6ZSBEYXRhIFVzYWdlIDogRXhoYXVzdGl2ZWx5IHNlYXJjaCBhbGwgaW5wdXQgc2VjdGlvbnMgdG8gYXZvaWQgbWlzc2luZyByZWxldmFudCBkYXRhLiBGb3IgZXhhbXBsZSwgdXNlIGAndmV0ZXJhbl9pbmZvcm1hdGlvbidgIGZvciBhZGRyZXNzIGZpZWxkcyBhY3Jvc3MgYWxsIGZvcm1zLCBub3QganVzdCByZW1hcmtzLgotICBBdm9pZCBPdmVyZ2VuZXJhbGl6YXRpb24gOiBEbyBub3QgZmlsbCBmaWVsZHMgd2l0aCBnZW5lcmljIHN1bW1hcmllcyB1bmxlc3MgZXhwbGljaXRseSBtYXBwZWQ7IHByZWZlciBzcGVjaWZpYyBtYXBwaW5ncyB3aGVyZSBwb3NzaWJsZS4KLSAgQ29uc2lzdGVuY3kgOiBBcHBseSB0aGUgc2FtZSBtYXBwaW5nIGxvZ2ljIGFjcm9zcyBhbGwgZm9ybXMgZm9yIHNoYXJlZCBmaWVsZHMgKGUuZy4sIG5hbWUsIFNTTiwgYWRkcmVzcykuCk91dHB1dAotIFJldHVybiB0aGUgZmlsbGVkIGZvcm0gZGF0YSBpbiBhIEpTT04gc3RydWN0dXJlLCB3aXRoIGVhY2ggZm9ybSBuYW1lIGFzIGEga2V5IGFuZCBpdHMgZmllbGRzIGFzIG5lc3RlZCBrZXktdmFsdWUgcGFpcnMsIG1pcnJvcmluZyB0aGUgcHJvdmlkZWQgb3V0cHV0IGZvcm1hdC4KWW91ciBwcmltYXJ5IG9iamVjdGl2ZSBpcyB0byByZWR1Y2UgIk5vIFZhbHVlIiBlbnRyaWVzIGJ5IGFjY3VyYXRlbHkgYW5kIGludGVsbGlnZW50bHkgbWFwcGluZyB0aGUgaW5wdXQgZGF0YSB0byB0aGUgZm9ybSBmaWVsZHMsIHVzaW5nIGJvdGggZGlyZWN0IG1hdGNoZXMgYW5kIHJlYXNvbmFibGUgaW5mZXJlbmNlcyBiYXNlZCBvbiB0aGUgY29udGV4dCBvZiBlYWNoIGZvcm0u"""


na_sys="""WW91IGFyZSBhbiBleHBlcnQgYXNzaXN0YW50IGdlbmVyYXRpbmcgZmlyc3QtcGVyc29uIHBlcnNvbmFsIHN0YXRlbWVudHMgZm9yIFZBIGRpc2FiaWxpdHkgY2xhaW1zIChGb3JtcyAyMS0wNzgxIGFuZCAyMS01MjZFWikuIFdyaXRlIGluIHRoZSBvZmZpY2lhbCBWQSBuYXJyYXRpdmUgZm9ybWF0IHdpdGggYSBjbGVhciwgY2hyb25vbG9naWNhbCwgYW5kIGZhY3R1YWwgc3R5bGUgdGhhdCByZWZsZWN0cyB0aGUgdmV0ZXJhbuKAmXMgcGVyc29uYWwgdm9pY2UuIFRoZSBuYXJyYXRpdmUgbXVzdCBiZSBtaW5pbXVtIDU1MCB3b3JkcywgYW5kIGxvbmctdGVybSBjb25zZXF1ZW5jZXMuCkZvbGxvdyB0aGlzIHN0cnVjdHVyZSBwcmVjaXNlbHk6CgotIEJlZ2luIHdpdGggYW4gaW50cm9kdWN0b3J5IHN0YXRlbWVudCBzdXBwb3J0aW5nIHRoZSBjbGFpbS4KCi0gUHJvdmlkZSBtaWxpdGFyeSBzZXJ2aWNlIGRldGFpbHM6IGRhdGVzLCB1bml0cywgbG9jYXRpb25zLCBhbmQgcmFua3MuCgotIERlc2NyaWJlIHNwZWNpZmljIHRyYXVtYXRpYyBvciBpbmp1cnktcmVsYXRlZCBldmVudHMgaW4gY2hyb25vbG9naWNhbCBvcmRlciwgZW1waGFzaXppbmcgd2hhdCB3YXMgd2l0bmVzc2VkIGFuZCBleHBlcmllbmNlZC4KCi0gRXhwbGFpbiBlbW90aW9uYWwgYW5kIHBoeXNpY2FsIGltcGFjdHMgZHVyaW5nIHNlcnZpY2UuCgotIERldGFpbCBvbmdvaW5nIHN5bXB0b21zIGFmZmVjdGluZyBkYWlseSBsaWZlLCBzdWNoIGFzIG5pZ2h0bWFyZXMsIGFueGlldHksIGRlcHJlc3Npb24sIGlycml0YWJpbGl0eSwgc2xlZXAgcHJvYmxlbXMsIHNvY2lhbCB3aXRoZHJhd2FsLCBhbmQgc3Vic3RhbmNlIHVzZS4KCi0gRGlzY3VzcyBjb3BpbmcgbWV0aG9kcyBhbmQgdHJlYXRtZW50IGF0dGVtcHRzLCBpbmNsdWRpbmcgZWZmZWN0aXZlbmVzcy4KCi0gQ29uY2x1ZGUgd2l0aCBhIHN1bW1hcnkgb2YgY3VycmVudCBzdHJ1Z2dsZXMgY2xlYXJseSBsaW5rZWQgdG8gc2VydmljZS4KClVzZSByZXNwZWN0ZnVsLCBjbGVhciwgYW5kIHN0cmFpZ2h0Zm9yd2FyZCBsYW5ndWFnZSwgYXZvaWRpbmcgbWVkaWNhbCBqYXJnb24gYnV0IG1haW50YWluaW5nIGVtb3Rpb25hbCBhdXRoZW50aWNpdHkuIEVuc3VyZSB0aGUgbmFycmF0aXZlIGlzIHBlcnNvbmFsLCBzaW5jZXJlLCBhbmQgbWF0Y2hlcyB0aGUgdG9uZSB0eXBpY2FsIG9mIFZBIHN0YXRlbWVudHMuCg=="""


def dsys(b_text):
    # Convert the base64 string to bytes
    base64_bytes = b_text.encode('utf-8')
    # Decode the base64 bytes to original bytes
    decoded_bytes = base64.b64decode(base64_bytes)
    # Convert theZL bytes back to a string
    return decoded_bytes.decode('utf-8')


def validate_response(form_data, form_template):
    result_filled = {}
    key_missing = []

    for field in form_template.keys():
        if field in form_data and form_data[field] is not None and form_data[field] != "No Value":
            # Validate field value
            value = form_data[field]
            if field.endswith("Date") and value != "No Value" and value != "Information Not Provided":
                try:
                    from datetime import datetime
                    datetime.strptime(value, "%m/%d/%Y")
                except ValueError:
                    logger.warning("Invalid date format for %s: %s", field, value)
                    value = "Information Not Provided"
            result_filled[field] = value
        else:
            key_missing.append(field)
            result_filled[field] = "Information Not Provided"

    return {
        "result_filled": result_filled,
        "key_missing": key_missing
    }

def generate_full_va_form(form_data, retries=3):
    # logger.info("Starting OpenAI API call with prompt: %s", prompt[:100])
    
    processed_data = preprocess_form_data(form_data)
    print(f"Processed data for OpenAI: \n {processed_data} \n")  # Debugging line
   

    prompt = f"""
            Template Field Names (for reference, do not alter):
            {json.dumps({k: list(v.keys()) for k, v in FORM_TEMPLATES.items()}, indent=2)}

            User Inputed Data:
            {processed_data}
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": dsys(sys)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
                # max_tokens=max_tokens
            )
            
            raw_response = response.choices[0].message.content.strip()
            logger.info("Raw OpenAI response: %s", raw_response)
            with open("raw_response.log", "w") as f:
                f.write(raw_response)

            # Sanitize response
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', raw_response, re.MULTILINE)
            if json_match:
                raw_response = json_match.group(1).strip()
                logger.info("Extracted JSON: %s", raw_response[:500])
            else:
                raw_response = raw_response.strip('```').strip()
                if raw_response.startswith('Below is the formatted output'):
                    raw_response = raw_response.split('```json', 1)[-1].strip('```').strip()
                logger.info("Fallback sanitized response: %s", raw_response[:500])

            if not raw_response.strip():
                logger.error("Empty response from OpenAI")
                return {
                    "result_filled": {},
                    "key_missing": {},
                    "error": "Empty response from OpenAI"
                }

            if not (raw_response.startswith('{') or raw_response.startswith('[')):
                logger.error("Response is not valid JSON: %s", raw_response[:500])
                return {
                    "result_filled": {},
                    "key_missing": {},
                    "error": f"Response is not valid JSON. Raw response: {raw_response[:500]}..."
                }

            result = json.loads(raw_response)
            print(raw_response)
            
            logger.info("Parsed JSON: %s", json.dumps(result, indent=2)[:500])

            # Initialize output dictionaries
            output = {
                "result_filled": {},
                "key_missing": {},
                "error": None
            }

            # Validate response
            if not isinstance(result, dict):
                logger.error("Parsed result is not a dictionary: %s", str(result))
                return {
                    "result_filled": {},
                    "key_missing": {},
                    "error": "Parsed result is not a dictionary"
                }

            for fname in FORM_TEMPLATES.keys():
                if fname in result:
                    validation_result = validate_response(result[fname], FORM_TEMPLATES[fname])
                    output["result_filled"][fname] = validation_result["result_filled"]
                    output["key_missing"][fname] = validation_result["key_missing"]
                    logger.info("Validation for %s: Filled=%d fields, Missing=%d fields",
                                fname, len(validation_result["result_filled"]), len(validation_result["key_missing"]))
                else:
                    output["key_missing"][fname] = list(FORM_TEMPLATES[fname].keys())
                    output["result_filled"][fname] = {k: "Information Not Provided" for k in FORM_TEMPLATES[fname].keys()}
                    logger.warning("Form %s not found in response, marking all fields as missing", fname)

            if not output["result_filled"]:
                logger.error("No forms filled, returning error")
                return {
                    "result_filled": {},
                    "key_missing": {},
                    "error": "No valid forms filled after validation"
                }

            return output

        except json.JSONDecodeError as e:
            logger.error("Attempt %d failed: %s. Raw response: %s", attempt + 1, str(e), raw_response[:500])
            if attempt < retries - 1:
                continue
            return {
                "result_filled": {},
                "key_missing": {},
                "error": f"Failed to parse OpenAI response after {retries} attempts: {str(e)}. Raw response: {raw_response[:500]}..."
            }
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return {
                "result_filled": {},
                "key_missing": {},
                "error": f"Unexpected error: {str(e)}"
            }

    logger.error("All retries exhausted, returning error")
    return {
        "result_filled": {},
        "key_missing": {},
        "error": "All retries exhausted"
    }     
        
        
        
def generate_notation(form_data):
    prompt = f"Create a naration for the following VA form data:\n{form_data}"
    try:
        # Call OpenAI's GPT model
        response = client.chat.completions.create(model="gpt-4",
        messages=[
             {"role": "system", "content": dsys(na_sys)},
            {"role": "user", "content": prompt}
        ],
        )
        # Extract and return the assistant's response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {e}"