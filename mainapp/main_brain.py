import json
from openai import OpenAI
import os
from dotenv import load_dotenv
from mainapp.template import FORM_TEMPLATES

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_SUMMARY_API_KEY"))


def get_form_template(form_name):
    if form_name:
        return FORM_TEMPLATES.get(form_name, {})
    return FORM_TEMPLATES  # Return all templates if form_name is empty

def generate_full_va_form(form_data):
    try:
        # Extract form name from form_data
        form_name = form_data.get("pdf", "")
        form_template = get_form_template(form_name)
        
        if not form_template:
            return {"error": f"No templates found for {form_name or 'any form'}"}

        # Prepare prompt based on whether a single template or all templates are used
        if form_name:
            # Single form case
            prompt = f"""You are a VA form processing expert. Accurately populate the VA form template for {form_name} using the provided data. 
Maintain the original JSON structure and all keys from the template. 
Replace "No Value" with appropriate values from the input data where available. 
Combine related fields when appropriate (e.g., SSN parts into a full SSN). 
If no data is provided for a field, retain "No Value" or infer reasonable defaults where applicable, ensuring compliance with VA form requirements.
Do not invent data unless explicitly provided in the input.

Input Data:
{json.dumps(form_data, indent=2)}

Return ONLY the completed JSON with the original structure of the {form_name} template:"""
        else:
            # All templates case
            prompt = f"""You are a VA form processing expert. Accurately populate all available VA form templates using the provided data. 
The templates include: {', '.join(FORM_TEMPLATES.keys())}. 
For each template, maintain the original JSON structure and all keys. 
Replace "No Value" with appropriate values from the input data where available. 
Combine related fields when appropriate (e.g., SSN parts into a full SSN). 
If no data is provided for a field, retain "No Value" or infer reasonable defaults where applicable, ensuring compliance with VA form requirements.
Do not invent data unless explicitly provided in the input.

Input Data:
{json.dumps(form_data, indent=2)}

Return a JSON object where each key is a form name (e.g., 'vba-21-4138-are.pdf') and the value is the completed JSON with the original structure of that form's template:"""

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a VA form processing expert. Strictly follow the template structure and VA form requirements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content.strip())
    
    except Exception as e:
        return {"error": str(e)}