import os
import zeep
from datetime import datetime
from lxml import etree

# Function to validate the WSDL file
def validate_wsdl(wsdl_url):
    try:
        client = zeep.Client(wsdl_url)
        print("WSDL is valid.")
        return client
    except Exception as e:
        print(f"Error validating WSDL: {e}")
        return None

# Function to parse WSDL and extract detailed documentation
def parse_wsdl(wsdl_url, output_directory):
    client = validate_wsdl(wsdl_url)
    if client is None:
        return

    wsdl_data = []
    try:
        # Extract services, ports, and operations
        for service_name, service in client.wsdl.services.items():
            service_details = {
                "service": service_name,
                "ports": []
            }

            for port_name, port in service.ports.items():
                port_details = {
                    "port": port_name,
                    "operations": []
                }

                for operation_name, operation in port.binding._operations.items():
                    try:
                        operation_details = {
                            "operation": operation_name,
                            "documentation": getattr(operation, 'documentation', "No documentation available"),
                            "input": [],
                            "output": [],
                            "soap_action": getattr(operation, 'soapaction', "No SOAPAction available")
                        }

                        # Extract input parameters
                        if hasattr(operation, "input") and operation.input:
                            try:
                                input_params = operation.input.signature().parameters.values()
                                for param in input_params:
                                    operation_details["input"].append({
                                        "name": param.name,
                                        "type": str(param.type),
                                        "required": "Yes"  # Assuming required
                                    })
                            except AttributeError:
                                operation_details["input"].append({
                                    "name": "Unknown",
                                    "type": "Unknown",
                                    "required": "Unknown"
                                })

                        # Extract output parameters
                        if hasattr(operation, "output") and operation.output:
                            operation_details["output"] = {"type": str(operation.output.type)}
                        else:
                            operation_details["output"] = {"type": "Unknown"}

                        port_details["operations"].append(operation_details)
                    except Exception as e:
                        print(f"Skipping operation {operation_name} due to an error: {e}")

                service_details["ports"].append(port_details)

            wsdl_data.append(service_details)

        # Extract types (ComplexTypes and SimpleTypes)
        types = []
        try:
            if hasattr(client.wsdl.types, 'schemas'):
                for schema in client.wsdl.types.schemas:
                    for name, schema_type in schema.elements.items():
                        type_details = {
                            "type": name.localname,
                            "elements": {}
                        }
                        if hasattr(schema_type, "type") and schema_type.type:
                            if hasattr(schema_type.type, "elements"):
                                type_details["elements"] = {
                                    el.name: str(el.type) for el in schema_type.type.elements
                                }
                            else:
                                type_details["elements"] = {"Unknown": str(schema_type.type)}
                        types.append(type_details)
        except Exception as e:
            print(f"Error extracting types: {e}")

        # Create both WSDL-styled and human-readable documentation
        create_documentation(wsdl_data, types, output_directory, "wsdl-styled")
        create_human_readable_documentation(wsdl_data, types, output_directory)

    except Exception as e:
        print(f"Error parsing WSDL file: {e}")


# Function to create WSDL-styled plain text documentation
def create_documentation(services, types, output_directory, doc_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_directory, f"wsdl_documentation_{timestamp}.txt")

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("WSDL Documentation\n")
            file.write("=" * 50 + "\n")
            
            for service in services:
                file.write(f"<service name=\"{service['service']}\">\n")
                
                for port in service["ports"]:
                    file.write(f"  <port name=\"{port['port']}\" binding=\"tns:{service['service']}Binding\">\n")
                    file.write(f"    <operations>\n")
                    for operation in port["operations"]:
                        file.write(f"      <operation name=\"{operation['operation']}\">\n")
                        file.write(f"        <documentation>{operation['documentation']}</documentation>\n")
                        file.write(f"        <input>\n")
                        for inp in operation["input"]:
                            file.write(f"          <part name=\"{inp['name']}\" type=\"{inp['type']}\" required=\"{inp['required']}\"/>\n")
                        file.write(f"        </input>\n")
                        file.write(f"        <output>\n")
                        if operation["output"]:
                            file.write(f"          <part type=\"{operation['output']['type']}\"/>\n")
                        else:
                            file.write(f"          <part type=\"Unknown\"/>\n")
                        file.write(f"        </output>\n")
                        file.write(f"        <soapAction>{operation['soap_action']}</soapAction>\n")
                        file.write(f"      </operation>\n")
                    file.write(f"    </operations>\n")
                    file.write(f"  </port>\n")

                file.write(f"</service>\n")

            file.write("\n<types>\n")
            for type_ in types:
                file.write(f"  <type name=\"{type_['type']}\">\n")
                for element_name, element_type in type_["elements"].items():
                    file.write(f"    <element name=\"{element_name}\" type=\"{element_type}\"/>\n")
                file.write(f"  </type>\n")
            file.write("</types>\n")

        print(f"Documentation saved successfully to {file_path}")
    except Exception as e:
        print(f"Error writing documentation file: {e}")


# Function to create human-readable documentation (similar to previous format)
def create_human_readable_documentation(services, types, output_directory):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_directory, f"human_readable_documentation_{timestamp}.txt")

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("WSDL Documentation\n")
            file.write("=" * 50 + "\n")

            for service in services:
                file.write(f"Service: {service['service']}\n")
                for port in service["ports"]:
                    file.write(f"  Port: {port['port']}\n")

                    file.write("  Operations:\n")
                    for operation in port["operations"]:
                        file.write(f"    Operation: {operation['operation']}\n")
                        file.write(f"      Documentation: {operation['documentation']}\n")
                        file.write(f"      Input:\n")
                        for inp in operation["input"]:
                            file.write(f"        - {inp['name']} ({inp['type']}) [Required: {inp['required']}]\n")
                        file.write(f"      Output:\n")
                        if operation["output"]:
                            file.write(f"        - {operation['output']['type']}\n")
                        else:
                            file.write(f"        - None\n")
                        file.write(f"      SOAPAction: {operation['soap_action']}\n")
                file.write("\n")

            # Write types section
            file.write("Types\n")
            file.write("=" * 50 + "\n")
            for type_ in types:
                file.write(f"Type: {type_['type']}\n")
                for element_name, element_type in type_["elements"].items():
                    file.write(f"  - {element_name}: {element_type}\n")
                file.write("\n")

        print(f"Human-readable documentation saved successfully to {file_path}")
    except Exception as e:
        print(f"Error writing documentation file: {e}")


# Main function to execute the script
def main():
    wsdl_url = input("Enter WSDL URL or file path: ").strip()
    output_directory = input("Enter output directory: ").strip()

    print(f"Attempting to load WSDL URI: {wsdl_url}")
    parse_wsdl(wsdl_url, output_directory)


if __name__ == "__main__":
    main()
