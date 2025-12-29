"""
Context Unpacker - LangBuilder Custom Component

Extracts individual fields from merged context data and outputs
them as separate Message values for use in Prompt Templates.

This component solves the problem where DataOperations "Combine"
produces a complex merged object, but Prompt Template variables
need individual Message inputs.

Author: CloudGeometry
Project: Carter's Agents - Content Engine
"""

from langbuilder.custom import Component
from langbuilder.inputs.inputs import HandleInput
from langbuilder.io import Output
from langbuilder.schema import Data
from langbuilder.schema.message import Message


class ContextUnpacker(Component):
    """
    Extracts individual fields from merged context data.

    Takes a combined Data object (from DataOperations Combine) and
    outputs individual Message values for each field needed by
    downstream Prompt Templates and Jinja2 Renderers.
    """

    display_name = "Context Unpacker"
    description = "Extracts individual fields from merged context data for template variables"
    icon = "unplug"
    name = "ContextUnpacker"

    inputs = [
        HandleInput(
            name="context_data",
            display_name="Context Data",
            input_types=["Data"],
            required=True,
            info="Merged context data from DataOperations Combine"
        )
    ]

    outputs = [
        Output(name="lead_name", display_name="Lead Name", method="get_lead_name"),
        Output(name="role", display_name="Role", method="get_role"),
        Output(name="company", display_name="Company", method="get_company"),
        Output(name="industry", display_name="Industry", method="get_industry"),
        Output(name="service_type", display_name="Service Type", method="get_service_type"),
        Output(name="annual_cloud_spend", display_name="Annual Cloud Spend", method="get_spend"),
        Output(name="calculated_savings", display_name="Calculated Savings", method="get_savings"),
        Output(name="contact_id", display_name="Contact ID", method="get_contact_id"),
    ]

    def _extract_data(self, value) -> dict:
        """Convert input to dictionary format."""
        if value is None:
            return {}
        if hasattr(value, 'data') and isinstance(value.data, dict):
            return value.data
        if isinstance(value, dict):
            return value
        return {}

    def _get_field(self, *keys, default="") -> str:
        """
        Extract field from potentially nested/merged data structure.

        Handles both flat structures and arrays created by Combine operation.
        Tries multiple key paths to find the value.
        """
        data = self._extract_data(self.context_data)

        for key in keys:
            # Try direct access first
            if key in data:
                value = data[key]
                # Handle arrays from Combine operation
                if isinstance(value, list):
                    # Find first non-empty value in array
                    for item in value:
                        if item and str(item) not in ['None', 'null', '']:
                            return str(item)
                elif value and str(value) not in ['None', 'null', '']:
                    return str(value)

            # Try nested in 'result' (from API responses)
            if 'result' in data:
                result = data['result']
                if isinstance(result, list):
                    for r in result:
                        if isinstance(r, dict) and key in r:
                            return str(r[key])
                        if isinstance(r, dict) and 'properties' in r and key in r['properties']:
                            return str(r['properties'][key])
                elif isinstance(result, dict):
                    if key in result:
                        return str(result[key])
                    if 'properties' in result and key in result['properties']:
                        return str(result['properties'][key])

            # Try in nested 'data' field
            if 'data' in data and isinstance(data['data'], dict):
                if key in data['data']:
                    return str(data['data'][key])

        return default

    def get_lead_name(self) -> Message:
        """Extract lead name (firstname + lastname or lead_name field)."""
        # Try firstname + lastname first
        first = self._get_field('firstname')
        last = self._get_field('lastname')

        if first or last:
            name = f"{first} {last}".strip()
            self.log(f"Lead name from firstname/lastname: {name}")
            return Message(text=name)

        # Fall back to lead_name field
        name = self._get_field('lead_name', 'name')
        self.log(f"Lead name from field: {name}")
        return Message(text=name)

    def get_role(self) -> Message:
        """Extract role/job title."""
        role = self._get_field('jobtitle', 'role', 'title', 'job_title')
        self.log(f"Role: {role}")
        return Message(text=role)

    def get_company(self) -> Message:
        """Extract company name."""
        company = self._get_field('company', 'name', 'company_name')
        self.log(f"Company: {company}")
        return Message(text=company)

    def get_industry(self) -> Message:
        """Extract industry."""
        industry = self._get_field('industry', 'hs_industry')
        self.log(f"Industry: {industry}")
        return Message(text=industry)

    def get_service_type(self) -> Message:
        """Extract service type from webhook data."""
        service = self._get_field('service_type', 'service')
        self.log(f"Service type: {service}")
        return Message(text=service)

    def get_spend(self) -> Message:
        """Extract annual cloud spend."""
        spend = self._get_field('annual_cloud_spend', 'annualrevenue', 'spend')
        self.log(f"Annual spend: {spend}")
        return Message(text=spend)

    def get_savings(self) -> Message:
        """Extract calculated savings."""
        savings = self._get_field('calculated_savings', 'savings')
        self.log(f"Calculated savings: {savings}")
        return Message(text=savings)

    def get_contact_id(self) -> Message:
        """Extract contact ID."""
        contact_id = self._get_field('contact_id', 'id', 'hs_object_id')
        self.log(f"Contact ID: {contact_id}")
        return Message(text=contact_id)
