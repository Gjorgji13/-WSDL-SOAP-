# WSDL Documentation Generator

This project parses Web Services Description Language (WSDL) files and generates documentation in both WSDL-styled and human-readable formats.  It's designed to help developers understand and interact with SOAP-based web services.

## Features

*   **WSDL Parsing:**  Parses WSDL files using the `zeep` library.  Performs basic WSDL validation.
*   **Documentation Generation:**  Creates two types of documentation:
    *   **WSDL-styled Documentation:**  This output mimics the structure of a WSDL file, embedding parsed data within WSDL-like tags.
    *   **Human-Readable Documentation:** A more easily understood format with clear descriptions of services, ports, operations, inputs, outputs, and types.
*   **Data Extraction:** Extracts key information including:
    *   Service names
    *   Port names
    *   Operation names
    *   Documentation for operations
    *   Input and output parameters (names, types, required status)
    *   SOAP Actions
    *   Complex and simple types

## Prerequisites

*   **Python 3.7+**
*   **Required Libraries:**
    *   `zeep`: For parsing the WSDL file.
    *   `lxml`: For XML processing.
    *   Other dependencies handled by `zeep`

You can install the required libraries using pip:

```bash
pip install zeep lxml
