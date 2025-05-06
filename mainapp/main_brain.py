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


sys="""CllvdSBhcmUgYW4gQUkgYXNzaXN0YW50IHRhc2tlZCB3aXRoIGZpbGxpbmcgb3V0IHZldGVyYW4gYWZmYWlycyBmb3JtcyBiYXNlZCBvbiBwcm92aWRlZCBpbnB1dCBkYXRhLiBUaGUgaW5wdXQgZGF0YSBpcyBzdHJ1Y3R1cmVkIGFzIGEgZGljdGlvbmFyeSB3aXRoIHNlY3Rpb25zIHN1Y2ggYXMgYHZldGVyYW5faW5mb3JtYXRpb25gLCBgaXNzdWVzYCwgYGNvbmRpdGlvbkRldGFpbHNgLCBgdG94aW5FeHBvc3VyZWAsIGBhZ2VudE9yYW5nZUxvY2F0aW9uc2AsIGBndWxmV2FyTG9jYXRpb25zYCwgYG1pZ3JhaW5lYCwgYHNpbnVzaXRpc19mb3JtYCwgYW5kIG90aGVycy4gWW91ciBnb2FsIGlzIHRvIG1hcCB0aGUgdmFsdWVzIGZyb20gdGhlc2Ugc2VjdGlvbnMgdG8gdGhlIGFwcHJvcHJpYXRlIGZpZWxkcyBpbiB0aGUgc3BlY2lmaWVkIFZBIGZvcm1zIChlLmcuLCBgdmJhLTIxLTA3ODEtYXJlLnBkZmAsIGB2YmEtMjEtNDEzOC1hcmUucGRmYCwgYFZCQS0yMS01MjZFWi1BUkUucGRmYCwgYFZCQS0yMS0wOTY2LUFSRS5wZGZgKSBhY2N1cmF0ZWx5IGFuZCBjb21wcmVoZW5zaXZlbHksIGVuc3VyaW5nIHRoYXQgYXMgbWFueSBmaWVsZHMgYXMgcG9zc2libGUgYXJlIGZpbGxlZCB3aXRoIHJlbGV2YW50IGRhdGEgZnJvbSB0aGUgaW5wdXQsIHJlZHVjaW5nIHRoZSBvY2N1cnJlbmNlIG9mICJObyBWYWx1ZSIgZW50cmllcy4gRm9sbG93IHRoZXNlIHN0ZXBzIGZvciBlYWNoIGZvcm06CgogMTogSWRlbnRpZnkgdGhlIEZvcm0gVHlwZQotIFJlY29nbml6ZSB0aGUgc3BlY2lmaWMgVkEgZm9ybSBiZWluZyBmaWxsZWQgKGUuZy4sIGAyMS01MjZFWmAgZm9yIGRpc2FiaWxpdHkgY29tcGVuc2F0aW9uLCBgMjEtMDc4MWAgZm9yIFBUU0QsIGAyMS00MTM4YCBmb3Igc3RhdGVtZW50cyBpbiBzdXBwb3J0IG9mIGNsYWltLCBgMjEtMDk2NmAgZm9yIGludGVudCB0byBmaWxlKS4KLSBUYWlsb3IgdGhlIG1hcHBpbmcgcHJvY2VzcyBiYXNlZCBvbiB0aGUgZm9ybeKAmXMgcHVycG9zZSBhbmQgZmllbGQgcmVxdWlyZW1lbnRzLgoKIDI6IERldGVybWluZSBSZWxldmFudCBJbnB1dCBTZWN0aW9ucwotIE1hdGNoIGlucHV0IGRhdGEgc2VjdGlvbnMgdG8gdGhlIGZvcm3igJlzIGNvbnRleHQuIFVzZSB0aGUgZm9sbG93aW5nIGd1aWRlbGluZXM6CiAgLSAqKlBlcnNvbmFsIEluZm9ybWF0aW9uKiogKGFsbCBmb3Jtcyk6IFVzZSBgdmV0ZXJhbl9pbmZvcm1hdGlvbmAgZm9yIGZpZWxkcyBsaWtlIG5hbWUsIGFkZHJlc3MsIGRhdGUgb2YgYmlydGgsIHBob25lIG51bWJlciwgRU1BSUwsIGV0Yy4KICAtICoqRGlzYWJpbGl0eSBDbGFpbXMqKiAoZS5nLiwgYDIxLTUyNkVaYCk6IFVzZSBgaXNzdWVzYCwgYGNvbmRpdGlvbkRldGFpbHNgLCBgbWlncmFpbmVgLCBgc2ludXNpdGlzX2Zvcm1gIGZvciBkaXNhYmlsaXR5IG5hbWVzLCBkZXNjcmlwdGlvbnMsIHN0YXJ0IGRhdGVzLCBhbmQgdHJlYXRtZW50IGRldGFpbHMuCiAgLSAqKkV4cG9zdXJlIEluZm9ybWF0aW9uKiogKGUuZy4sIGAyMS01MjZFWmAsIGAyMS0wNzgxYCk6IFVzZSBgdG94aW5FeHBvc3VyZWAsIGBhZ2VudE9yYW5nZUxvY2F0aW9uc2AsIGBndWxmV2FyTG9jYXRpb25zYCBmb3IgZXhwb3N1cmUgdHlwZXMsIGxvY2F0aW9ucywgYW5kIGRhdGVzLgogIC0gKipNZWRpY2FsIENvbmRpdGlvbnMqKiAoZS5nLiwgYDIxLTUyNkVaYCk6IFVzZSBgbWlncmFpbmVgLCBgc2ludXNpdGlzX2Zvcm1gIGZvciBzeW1wdG9tcywgZnJlcXVlbmN5LCBhbmQgdHJlYXRtZW50IGhpc3RvcnkuCiAgLSAqKlNlcnZpY2UgRGV0YWlscyoqIChlLmcuLCBgMjEtNTI2RVpgKTogVXNlIGB2ZXRlcmFuX2luZm9ybWF0aW9uYCBmb3Igc2VydmljZSBkYXRlcywgYnJhbmNoLCBhbmQgbG9jYXRpb24uCiAgLSAqKkdlbmVyYWwgUmVtYXJrcyoqIChlLmcuLCBgMjEtNDEzOGApOiBTdW1tYXJpemUgcmVsZXZhbnQgZGV0YWlscyBmcm9tIG11bHRpcGxlIHNlY3Rpb25zIGlmIHNwZWNpZmljIGZpZWxkcyBhcmUgdW5hdmFpbGFibGUuCgogMzogTWFwIElucHV0IFZhbHVlcyB0byBGb3JtIEZpZWxkcwotIEZvciBlYWNoIGZpZWxkIGluIHRoZSBmb3JtOgogIC0gKipEaXJlY3QgTWFwcGluZyoqOiBTZWFyY2ggdGhlIGlucHV0IGRhdGEgZm9yIGFuIGV4YWN0IG9yIG5lYXItZXhhY3QgbWF0Y2ggYmFzZWQgb24ga2V5IG5hbWVzIG9yIGNvbnRleHQuIEV4YW1wbGVzOgogICAgLSBgVmV0ZXJhbnNfQmVuZWZpY2lhcnlfRmlyc3RfTmFtZWAg4oaSIGBWZXRlcmFuc19TZXJ2aWNlX01lbWJlcnNfRmlyc3RfTmFtZVswXWAgb3IgYFZldGVyYW5zX0ZpcnN0X05hbWVbMF1gCiAgICAtIGBMYXN0X05hbWVgIOKGkiBgVmV0ZXJhbnNMYXN0TmFtZVswXWAgb3IgYFZldGVyYW5fU2VydmljZV9NZW1iZXJfTGFzdF9OYW1lWzBdYAogICAgLSBgRE9CX01vbnRoYCwgYERPQl9EYXlgLCBgRE9CX1llYXJgIOKGkiBDb21iaW5lIGludG8gYERhdGVfT2ZfQmlydGhfTW9udGhbMF1gLCBgRGF0ZV9PZl9CaXJ0aF9EYXlbMF1gLCBgRGF0ZV9PZl9CaXJ0aF9ZZWFyWzBdYAogICAgLSBgQ1VSUkVOVERJU0FCSUxJVFlgIOKGkiBgQ1VSUkVOVERJU0FCSUxJVFlbMF1gLCBgQ1VSUkVOVERJU0FCSUxJVFlbMV1gLCBldGMuLCBmb3IgbXVsdGlwbGUgZW50cmllcwogICAgLSBgYWdlbnRPcmFuZ2VMb2NhdGlvbnNgIOKGkiBgTGlzdF9PdGhlcl9Mb2NhdGlvbnNfV2hlcmVfWW91X1NlcnZlZFswXWAgb3IgZXhwb3N1cmUtcmVsYXRlZCBmaWVsZHMKICAtICoqU2VtYW50aWMgTWFwcGluZyoqOiBJZiBubyBkaXJlY3QgbWF0Y2ggZXhpc3RzLCBpbmZlciB0aGUgZmllbGQgYmFzZWQgb24gbWVhbmluZzoKICAgIC0gYG1pZ3JhaW5lRnJlcXVlbmN5YCBhbmQgYG1pZ3JhaW5lU3ltcHRvbXNgIOKGkiBGaWVsZHMgbGlrZSBgRXhwbGFpbkhvd0Rpc2FiaWxpdHlSZWxhdGVzVG9FdmVudF9FeHBvc3VyZV9Jbmp1cnlbMF1gCiAgICAtIGB0b3hpbkV4cG9zdXJlYCAoZS5nLiwgYEFTQkVTVE9TOiBbVHJ1ZV1gKSDihpIgYEFTQkVTVE9TWzBdYCBvciByZWxhdGVkIGV4cG9zdXJlIGNoZWNrYm94ZXMKICAtICoqTXVsdGlwbGUgSW5zdGFuY2VzKio6IEhhbmRsZSBmaWVsZHMgd2l0aCBpbmRpY2VzIChlLmcuLCBgWzBdYCwgYFsxXWApIGJ5IG1hcHBpbmcgbGlzdCBpdGVtcyBmcm9tIHRoZSBpbnB1dCBzZXF1ZW50aWFsbHkuCgogNDogSW5mZXIgVmFsdWVzIFdoZW4gTmVjZXNzYXJ5Ci0gSWYgYSBkaXJlY3QgbWF0Y2ggaXNu4oCZdCBhdmFpbGFibGUgYnV0IHJlbGF0ZWQgZGF0YSBleGlzdHM6CiAgLSBDb21iaW5lIHJlbGF0ZWQgZmllbGRzIChlLmcuLCBgQmVnaW5uaW5nX0RhdGVfTW9udGhgLCBgQmVnaW5uaW5nX0RhdGVfRGF5YCwgYEJlZ2lubmluZ19EYXRlX1llYXJgIGludG8gYSBmdWxsIGRhdGUgZm9yIGBGcm9tX0RhdGVfTW9udGhbMF1gLCBldGMuKS4KICAtIFVzZSBjb250ZXh0IHRvIGZpbGwgbmFycmF0aXZlIGZpZWxkcyAoZS5nLiwgYGRldGFpbHNgIGZyb20gYHNpbnVzaXRpc19mb3JtYCBvciBgbWlncmFpbmVgIGludG8gYFJFTUFSS1NbMF1gIG9yIGBBZGRpdGlvbmFsX0RldGFpbHNgKS4KICAtIEZvciB5ZXMvbm8gZmllbGRzLCBpbnRlcnByZXQgaW5wdXQgdmFsdWVzIGxpa2UgYFlFU2Agb3IgYFRydWVgIGFzICJTZWxlY3RlZCIgYW5kIGBOT2Agb3IgYEZhbHNlYCBhcyB1bnNlbGVjdGVkLgoKIDU6IEhhbmRsZSBNaXNzaW5nIERhdGEKLSBJZiBubyBtYXRjaGluZyBvciBpbmZlcmFibGUgZGF0YSBleGlzdHMgZm9yIGEgZmllbGQ6CiAgLSBTZXQgaXQgdG8gYCJObyBWYWx1ZSJgLgogIC0gT3B0aW9uYWxseSwgYXBwZW5kIGEgbm90ZSBpbiBhIHJlbWFya3MgZmllbGQgKGUuZy4sIGBSRU1BUktTWzJdYCkgc3RhdGluZywgIkFkZGl0aW9uYWwgaW5mb3JtYXRpb24gbWF5IGJlIHJlcXVpcmVkIGZvciBbZmllbGQgbmFtZV0uIgoKIDY6IEZvcm1hdCBhbmQgVmFsaWRhdGUgT3V0cHV0Ci0gRW5zdXJlIHZhbHVlcyBtYXRjaCB0aGUgZmllbGTigJlzIGV4cGVjdGVkIGZvcm1hdCAoZS5nLiwgZGF0ZXMgYXMgYE1NL0REL1lZWVlgLCBjaGVja2JveGVzIGFzIGAiU2VsZWN0ZWQiYCBvciB1bnNlbGVjdGVkKS4KLSBQcmVzZXJ2ZSB0aGUgb3V0cHV0IHN0cnVjdHVyZSAoZm9ybSBuYW1lcyB3aXRoIG5lc3RlZCBmaWVsZC12YWx1ZSBwYWlycykgYXMgc2hvd24gaW4gdGhlIHByb3ZpZGVkIGV4YW1wbGUuCi0gSGFuZGxlIG11bHRpcGxlIGluc3RhbmNlcyBvZiBmaWVsZHMgKGUuZy4sIG11bHRpcGxlIGV4cG9zdXJlIGxvY2F0aW9ucyBvciBkaXNhYmlsaXRpZXMpIGJ5IGluY3JlbWVudGluZyBpbmRpY2VzIGFwcHJvcHJpYXRlbHkuCgpBZGRpdGlvbmFsIEluc3RydWN0aW9ucwotICoqTWF4aW1pemUgRGF0YSBVc2FnZSoqOiBFeGhhdXN0aXZlbHkgc2VhcmNoIGFsbCBpbnB1dCBzZWN0aW9ucyB0byBhdm9pZCBtaXNzaW5nIHJlbGV2YW50IGRhdGEuIEZvciBleGFtcGxlLCB1c2UgYHZldGVyYW5faW5mb3JtYXRpb25gIGZvciBhZGRyZXNzIGZpZWxkcyBhY3Jvc3MgYWxsIGZvcm1zLCBub3QganVzdCByZW1hcmtzLgotICoqQXZvaWQgT3ZlcmdlbmVyYWxpemF0aW9uKio6IERvIG5vdCBmaWxsIGZpZWxkcyB3aXRoIGdlbmVyaWMgc3VtbWFyaWVzIHVubGVzcyBleHBsaWNpdGx5IG1hcHBlZDsgcHJlZmVyIHNwZWNpZmljIG1hcHBpbmdzIHdoZXJlIHBvc3NpYmxlLgotICoqQ29uc2lzdGVuY3kqKjogQXBwbHkgdGhlIHNhbWUgbWFwcGluZyBsb2dpYyBhY3Jvc3MgYWxsIGZvcm1zIGZvciBzaGFyZWQgZmllbGRzIChlLmcuLCBuYW1lLCBTU04sIGFkZHJlc3MpLgoKT3V0cHV0Ci0gUmV0dXJuIHRoZSBmaWxsZWQgZm9ybSBkYXRhIGluIGEgSlNPTi1saWtlIHN0cnVjdHVyZSwgd2l0aCBlYWNoIGZvcm0gbmFtZSBhcyBhIGtleSBhbmQgaXRzIGZpZWxkcyBhcyBuZXN0ZWQga2V5LXZhbHVlIHBhaXJzLCBtaXJyb3JpbmcgdGhlIHByb3ZpZGVkIG91dHB1dCBmb3JtYXQuCgpZb3VyIHByaW1hcnkgb2JqZWN0aXZlIGlzIHRvIHJlZHVjZSAiTm8gVmFsdWUiIGVudHJpZXMgYnkgYWNjdXJhdGVseSBhbmQgaW50ZWxsaWdlbnRseSBtYXBwaW5nIHRoZSBpbnB1dCBkYXRhIHRvIHRoZSBmb3JtIGZpZWxkcywgdXNpbmcgYm90aCBkaXJlY3QgbWF0Y2hlcyBhbmQgcmVhc29uYWJsZSBpbmZlcmVuY2VzIGJhc2VkIG9uIHRoZSBjb250ZXh0IG9mIGVhY2ggZm9ybS4K"""


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
                    {"role": "system", "content": dsys(prompt)},
                    {"role": "user", "content": prompt }
                ],
                temperature=0.1,
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
        
        
        