"""
Export Service
Handles CSV and PDF export of analytics data
"""

import io
import csv
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import pandas as pd


class ExportService:
    """Service for exporting analytics data to various formats"""

    @staticmethod
    def flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
        """
        Flatten nested dictionary for CSV export

        Args:
            data: Dictionary to flatten
            parent_key: Parent key for recursion
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ExportService.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to comma-separated strings
                items.append((new_key, ", ".join(str(item) for item in v)))
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def export_to_csv(data: Dict[str, Any], report_type: str) -> bytes:
        """
        Export analytics data to CSV format

        Args:
            data: Analytics data to export
            report_type: Type of report (revenue, disputes, etc.)

        Returns:
            CSV file content as bytes
        """
        output = io.StringIO()

        # Flatten the data structure
        flat_data = ExportService.flatten_dict(data)

        # Create CSV writer
        writer = csv.writer(output)

        # Write header
        writer.writerow(["CreditBeast Analytics Report"])
        writer.writerow([f"Report Type: {report_type.replace('_', ' ').title()}"])
        writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        writer.writerow([])  # Empty row

        # Write data as key-value pairs
        writer.writerow(["Metric", "Value"])
        for key, value in flat_data.items():
            formatted_key = key.replace("_", " ").title()
            writer.writerow([formatted_key, value])

        # Convert to bytes
        csv_content = output.getvalue()
        return csv_content.encode('utf-8')

    @staticmethod
    def export_to_csv_table(data_list: List[Dict[str, Any]], report_type: str) -> bytes:
        """
        Export list of records to CSV table format using pandas

        Args:
            data_list: List of records to export
            report_type: Type of report

        Returns:
            CSV file content as bytes
        """
        if not data_list:
            return b"No data available"

        # Convert to pandas DataFrame
        df = pd.DataFrame(data_list)

        # Create output buffer
        output = io.StringIO()

        # Write header information
        output.write(f"CreditBeast Analytics Report\n")
        output.write(f"Report Type: {report_type.replace('_', ' ').title()}\n")
        output.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("\n")

        # Write DataFrame to CSV
        df.to_csv(output, index=False)

        # Convert to bytes
        return output.getvalue().encode('utf-8')

    @staticmethod
    def export_to_pdf(data: Dict[str, Any], report_type: str, org_name: str = "CreditBeast") -> bytes:
        """
        Export analytics data to PDF format

        Args:
            data: Analytics data to export
            report_type: Type of report (revenue, disputes, etc.)
            org_name: Organization name for branding

        Returns:
            PDF file content as bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Container for PDF elements
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e429f'),
            spaceAfter=12,
            spaceBefore=12
        )

        normal_style = styles['Normal']

        # Add title
        title = Paragraph(f"{org_name} Analytics Report", title_style)
        elements.append(title)

        # Add report metadata
        metadata = [
            ["Report Type:", report_type.replace("_", " ").title()],
            ["Generated:", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ]

        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(metadata_table)
        elements.append(Spacer(1, 20))

        # Process data sections
        def add_section(section_title: str, section_data: Any):
            """Add a section to the PDF"""
            # Section heading
            heading = Paragraph(section_title, heading_style)
            elements.append(heading)

            if isinstance(section_data, dict):
                # Create table from dictionary
                table_data = [[k.replace("_", " ").title(), str(v)]
                             for k, v in section_data.items()]

                if table_data:
                    table = Table(table_data, colWidths=[3*inch, 3*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ]))
                    elements.append(table)
            elif isinstance(section_data, list):
                # Handle list data
                for item in section_data:
                    para = Paragraph(f"• {str(item)}", normal_style)
                    elements.append(para)
            else:
                # Handle scalar values
                para = Paragraph(str(section_data), normal_style)
                elements.append(para)

            elements.append(Spacer(1, 12))

        # Add main data sections
        for key, value in data.items():
            section_title = key.replace("_", " ").title()
            add_section(section_title, value)

        # Add footer
        elements.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer = Paragraph(
            f"Generated by CreditBeast Analytics • {datetime.now().strftime('%Y')} • Confidential",
            footer_style
        )
        elements.append(footer)

        # Build PDF
        doc.build(elements)

        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()

        return pdf_content

    @staticmethod
    def export_analytics_report(
        data: Dict[str, Any],
        report_type: str,
        format: str,
        org_name: str = "CreditBeast"
    ) -> bytes:
        """
        Export analytics report in specified format

        Args:
            data: Analytics data
            report_type: Type of report
            format: Export format (csv or pdf)
            org_name: Organization name

        Returns:
            File content as bytes

        Raises:
            ValueError: If format is not supported
        """
        if format.lower() == "csv":
            return ExportService.export_to_csv(data, report_type)
        elif format.lower() == "pdf":
            return ExportService.export_to_pdf(data, report_type, org_name)
        else:
            raise ValueError(f"Unsupported export format: {format}")
