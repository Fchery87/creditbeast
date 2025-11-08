"""
Letter Templates Service
Provides dispute letter templates with variable substitution
"""

from typing import Dict, Any
from datetime import datetime


class LetterTemplates:
    """Dispute letter templates for different bureau types and dispute reasons"""

    # Bureau addresses
    BUREAU_ADDRESSES = {
        "equifax": {
            "name": "Equifax Information Services LLC",
            "address": "P.O. Box 740256\nAtlanta, GA 30374"
        },
        "experian": {
            "name": "Experian",
            "address": "P.O. Box 4500\nAllen, TX 75013"
        },
        "transunion": {
            "name": "TransUnion LLC",
            "address": "P.O. Box 2000\nChester, PA 19016"
        }
    }

    @staticmethod
    def get_standard_dispute_template() -> str:
        """Standard dispute letter template"""
        return """Date: {date}

{bureau_name}
{bureau_address}

Re: Request for Investigation of Inaccurate Information

Dear Sir/Madam,

I am writing to dispute the following information in my credit file. The items I dispute are also noted on the attached copy of my credit report.

DISPUTED ITEM INFORMATION:
Account Name: {account_name}
Account Number: {account_number_masked}
Dispute Type: {dispute_type}
Reason for Dispute: {dispute_reason}

This item is {dispute_basis} and I am requesting that it be removed or corrected. I am requesting that you {action_requested}.

Enclosed are copies of {supporting_documents} supporting my position. Please investigate this matter and {correction_requested} as soon as possible.

Under the Fair Credit Reporting Act (15 U.S.C. § 1681 et seq.), you are required to investigate and respond to this dispute within 30 days.

Sincerely,

{client_name}
{client_address}
{client_city}, {client_state} {client_zip}
{client_ssn_masked}
Date of Birth: {client_dob_masked}"""

    @staticmethod
    def get_inquiry_dispute_template() -> str:
        """Template for disputing inquiries"""
        return """Date: {date}

{bureau_name}
{bureau_address}

Re: Unauthorized Inquiry Dispute

Dear Sir/Madam,

I am writing to dispute the following unauthorized inquiry appearing on my credit report:

DISPUTED INQUIRY:
Creditor Name: {account_name}
Date of Inquiry: {inquiry_date}
Reason for Dispute: {dispute_reason}

I did not authorize this inquiry and request that it be removed from my credit report immediately. This inquiry is negatively affecting my credit score without my consent.

Under the Fair Credit Reporting Act (FCRA), I have the right to dispute inaccurate information. Please investigate this unauthorized inquiry and remove it from my credit file within 30 days.

Sincerely,

{client_name}
{client_address}
{client_city}, {client_state} {client_zip}
{client_ssn_masked}
Date of Birth: {client_dob_masked}"""

    @staticmethod
    def get_collection_dispute_template() -> str:
        """Template for disputing collections"""
        return """Date: {date}

{bureau_name}
{bureau_address}

Re: Dispute of Collection Account

Dear Sir/Madam,

I am writing to dispute a collection account that appears on my credit report:

COLLECTION ACCOUNT DETAILS:
Collection Agency: {account_name}
Account Number: {account_number_masked}
Amount: {collection_amount}
Reason for Dispute: {dispute_reason}

{dispute_basis}

I request that you conduct a thorough investigation of this collection account. If you cannot verify the accuracy and completeness of this information, it must be deleted from my credit report in accordance with the Fair Credit Reporting Act.

Please provide me with proof of verification once your investigation is complete. If this item cannot be verified, please remove it immediately.

Sincerely,

{client_name}
{client_address}
{client_city}, {client_state} {client_zip}
{client_ssn_masked}
Date of Birth: {client_dob_masked}"""

    @staticmethod
    def get_late_payment_dispute_template() -> str:
        """Template for disputing late payments"""
        return """Date: {date}

{bureau_name}
{bureau_address}

Re: Dispute of Late Payment Reporting

Dear Sir/Madam,

I am writing to dispute the late payment(s) being reported on my credit file for the following account:

ACCOUNT INFORMATION:
Creditor: {account_name}
Account Number: {account_number_masked}
Late Payment Date(s): {late_payment_dates}
Reason for Dispute: {dispute_reason}

{dispute_basis}

I request that you investigate this matter and correct the inaccurate late payment reporting. My payment history should accurately reflect my responsible management of this account.

Please conduct a full investigation and provide me with the results. If you cannot verify the accuracy of these late payment notations, they must be removed from my credit report.

Sincerely,

{client_name}
{client_address}
{client_city}, {client_state} {client_zip}
{client_ssn_masked}
Date of Birth: {client_dob_masked}"""

    @staticmethod
    def get_charge_off_dispute_template() -> str:
        """Template for disputing charge-offs"""
        return """Date: {date}

{bureau_name}
{bureau_address}

Re: Dispute of Charge-Off Account

Dear Sir/Madam,

I am disputing the following charge-off account appearing on my credit report:

CHARGE-OFF ACCOUNT:
Creditor: {account_name}
Account Number: {account_number_masked}
Charge-Off Amount: {charge_off_amount}
Charge-Off Date: {charge_off_date}
Reason for Dispute: {dispute_reason}

{dispute_basis}

Under the Fair Credit Reporting Act, you must investigate disputed items and verify their accuracy. I request that you conduct a thorough investigation of this charge-off. If you cannot verify all details of this account, it must be removed from my credit report.

Please respond with the results of your investigation within 30 days as required by law.

Sincerely,

{client_name}
{client_address}
{client_city}, {client_state} {client_zip}
{client_ssn_masked}
Date of Birth: {client_dob_masked}"""

    @classmethod
    def generate_letter(
        cls,
        dispute_data: Dict[str, Any],
        client_data: Dict[str, Any],
        organization_data: Dict[str, Any]
    ) -> str:
        """
        Generate a dispute letter based on dispute type

        Args:
            dispute_data: Dispute information (type, reason, account, etc.)
            client_data: Client information (name, address, SSN, DOB, etc.)
            organization_data: Organization branding/settings

        Returns:
            Formatted letter content
        """
        dispute_type = dispute_data.get("dispute_type", "").lower()
        bureau = dispute_data.get("bureau", "equifax").lower()

        # Select appropriate template
        if dispute_type == "inquiry":
            template = cls.get_inquiry_dispute_template()
        elif dispute_type in ["collection", "collections"]:
            template = cls.get_collection_dispute_template()
        elif dispute_type in ["late_payment", "late payment"]:
            template = cls.get_late_payment_dispute_template()
        elif dispute_type in ["charge_off", "charge-off", "chargeoff"]:
            template = cls.get_charge_off_dispute_template()
        else:
            template = cls.get_standard_dispute_template()

        # Get bureau information
        bureau_info = cls.BUREAU_ADDRESSES.get(bureau, cls.BUREAU_ADDRESSES["equifax"])

        # Mask sensitive data
        ssn = client_data.get("ssn", "")
        ssn_masked = f"XXX-XX-{ssn[-4:]}" if ssn and len(ssn) >= 4 else "XXX-XX-XXXX"

        dob = client_data.get("date_of_birth", "")
        if dob:
            try:
                dob_obj = datetime.fromisoformat(str(dob).replace('Z', '+00:00'))
                dob_masked = f"XX/XX/{dob_obj.year}"
            except:
                dob_masked = "XX/XX/XXXX"
        else:
            dob_masked = "XX/XX/XXXX"

        account_number = dispute_data.get("account_number", "")
        account_number_masked = f"XXXX{account_number[-4:]}" if account_number and len(account_number) >= 4 else "XXXX"

        # Prepare template variables
        variables = {
            "date": datetime.now().strftime("%B %d, %Y"),
            "bureau_name": bureau_info["name"],
            "bureau_address": bureau_info["address"],
            "account_name": dispute_data.get("account_name", "N/A"),
            "account_number_masked": account_number_masked,
            "dispute_type": dispute_data.get("dispute_type", "").replace("_", " ").title(),
            "dispute_reason": dispute_data.get("dispute_reason", ""),
            "dispute_basis": cls._get_dispute_basis(dispute_data),
            "action_requested": cls._get_action_requested(dispute_data),
            "correction_requested": cls._get_correction_requested(dispute_data),
            "supporting_documents": dispute_data.get("supporting_documents", "documentation"),
            "client_name": client_data.get("full_name", ""),
            "client_address": client_data.get("street_address", ""),
            "client_city": client_data.get("city", ""),
            "client_state": client_data.get("state", ""),
            "client_zip": client_data.get("zip_code", ""),
            "client_ssn_masked": ssn_masked,
            "client_dob_masked": dob_masked,
            # Additional fields for specific templates
            "inquiry_date": dispute_data.get("inquiry_date", "N/A"),
            "collection_amount": dispute_data.get("collection_amount", "N/A"),
            "charge_off_amount": dispute_data.get("charge_off_amount", "N/A"),
            "charge_off_date": dispute_data.get("charge_off_date", "N/A"),
            "late_payment_dates": dispute_data.get("late_payment_dates", "N/A"),
        }

        # Format the letter
        try:
            letter = template.format(**variables)
            return letter
        except KeyError as e:
            raise ValueError(f"Missing required variable for letter generation: {e}")

    @staticmethod
    def _get_dispute_basis(dispute_data: Dict[str, Any]) -> str:
        """Get the basis/explanation for the dispute"""
        reason = dispute_data.get("dispute_reason", "").lower()

        # Provide standard dispute basis language
        if "not mine" in reason or "not my" in reason:
            return "not my account and I never authorized it"
        elif "paid" in reason:
            return "inaccurate because this account has been paid in full"
        elif "incorrect" in reason or "inaccurate" in reason:
            return "reporting inaccurate information"
        elif "duplicate" in reason:
            return "a duplicate entry and should be removed"
        elif "unauthorized" in reason:
            return "unauthorized and I have no knowledge of this account"
        else:
            return "inaccurate and requires correction"

    @staticmethod
    def _get_action_requested(dispute_data: Dict[str, Any]) -> str:
        """Get the action being requested"""
        return "remove this item from my credit report or correct the inaccurate information"

    @staticmethod
    def _get_correction_requested(dispute_data: Dict[str, Any]) -> str:
        """Get the specific correction requested"""
        return "delete or correct the disputed information"
