import json
from zeep import Client

def get_type_details(xsd_type):
    """
    Recursively drills into a Zeep/XSD type to extract field names and types.
    """
    fields = {}
    
    # Handle ComplexTypes with sequences/choices/all indicators
    if hasattr(xsd_type, 'elements'):
        for name, element in xsd_type.elements:
            # Get the type name (e.g., 'CustomerIDType' or 'string')
            type_obj = element.type
            type_name = type_obj.name if hasattr(type_obj, 'name') else str(type_obj)
            
            # Check if optional
            is_optional = getattr(element, 'min_occurs', 1) == 0
            
            fields[name] = {
                "type": type_name,
                "required": not is_optional
            }
    return fields

def parse_wsdl_complex_types(wsdl_url):
    client = Client(wsdl_url)
    all_ops_data = []

    # Iterate through services and operations
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            for op_name, operation in port.binding._operations.items():
                
                # Extract Request structure
                req_fields = {}
                if operation.input and operation.input.body:
                    # Access the complex type of the input message
                    req_type = operation.input.body.type
                    req_fields = get_type_details(req_type)

                # Extract Response structure
                res_fields = {}
                if operation.output and operation.output.body:
                    res_type = operation.output.body.type
                    res_fields = get_type_details(res_type)

                op_payload = {
                    "operation": op_name,
                    "request_schema": req_fields,
                    "response_schema": res_fields,
                    "documentation": f"SOAP Operation: {op_name} for Canada Post Manifest API"
                }
                all_ops_data.append(op_payload)

    return all_ops_data

# Example Usage
wsdl_url = "https://www.canadapost-postescanada.ca/cpc/doc/en/business/developers/wsdl/manifest.wsdl"
data = parse_wsdl_complex_types(wsdl_url)

# Display what will be sent to Qdrant
print(json.dumps(data[1], indent=2)) # Showing GetManifestArtifactId