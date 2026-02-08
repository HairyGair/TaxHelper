"""
Professional Data Export Manager
Provides multiple export formats for Tax Helper data
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional
import json

# PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class ExportManager:
    """Centralized export functionality for all data types"""

    def __init__(self, session):
        self.session = session

    def export_to_csv(self, data: pd.DataFrame, filename: str) -> bytes:
        """Export DataFrame to CSV format"""
        return data.to_csv(index=False).encode('utf-8')

    def export_to_excel(self,
                       data_dict: Dict[str, pd.DataFrame],
                       filename: str,
                       include_summary: bool = True,
                       show_progress: bool = False) -> bytes:
        """
        Export multiple DataFrames to Excel with multiple sheets

        Args:
            data_dict: Dictionary of {sheet_name: DataFrame}
            filename: Output filename
            include_summary: Whether to include a summary sheet
            show_progress: Whether to show progress indicator
        """
        output = BytesIO()

        # Wrap in progress indicator if requested
        if show_progress:
            import streamlit as st
            with st.spinner(f"Generating Excel export with {len(data_dict)} sheets..."):
                return self._do_excel_export(output, data_dict, include_summary)
        else:
            return self._do_excel_export(output, data_dict, include_summary)

    def _do_excel_export(self, output: BytesIO, data_dict: Dict[str, pd.DataFrame],
                         include_summary: bool) -> bytes:
        """Internal method to perform Excel export"""
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Add summary sheet if requested
            if include_summary:
                summary_data = self._generate_summary(data_dict)
                summary_data.to_excel(writer, sheet_name='Summary', index=False)

            # Add each data sheet
            for sheet_name, df in data_dict.items():
                # Sanitize sheet name - Excel doesn't allow: / \ ? * [ ] :
                clean_sheet_name = sheet_name.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '(').replace(']', ')').replace(':', '-')
                # Excel sheet names max 31 chars
                clean_sheet_name = clean_sheet_name[:31]
                df.to_excel(writer, sheet_name=clean_sheet_name, index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets[clean_sheet_name]
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)

        output.seek(0)
        return output.getvalue()

    def export_to_pdf(self,
                     data: pd.DataFrame,
                     title: str,
                     filename: str,
                     metadata: Optional[Dict[str, str]] = None,
                     show_progress: bool = False) -> bytes:
        """
        Export DataFrame to professional PDF format

        Args:
            data: DataFrame to export
            title: Report title
            filename: Output filename
            metadata: Optional metadata (tax year, date range, etc.)
            show_progress: Whether to show progress indicator
        """
        if not PDF_AVAILABLE:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")

        if show_progress:
            import streamlit as st
            with st.spinner(f"Generating PDF report: {title}..."):
                return self._do_pdf_export(data, title, metadata)
        else:
            return self._do_pdf_export(data, title, metadata)

    def _do_pdf_export(self, data: pd.DataFrame, title: str,
                      metadata: Optional[Dict[str, str]] = None,
                      use_aurora_theme: bool = True) -> bytes:
        """Internal method to perform PDF export with optional Aurora theme"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=30, leftMargin=30,
                              topMargin=30, bottomMargin=30)

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        if use_aurora_theme:
            # Aurora-themed styles with purple/blue gradient colors
            title_style = ParagraphStyle(
                'AuroraTitle',
                parent=styles['Heading1'],
                fontSize=28,
                textColor=colors.HexColor('#8b5cf6'),  # Aurora purple
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            subtitle_style = ParagraphStyle(
                'AuroraSubtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#3b82f6'),  # Aurora blue
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        else:
            # Original style
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0077b6'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            subtitle_style = styles['Normal']

        # Add decorative header bar for Aurora theme
        if use_aurora_theme:
            # Add title
            elements.append(Paragraph(title, title_style))
            elements.append(Paragraph("UK Tax Helper - Professional Financial Report", subtitle_style))
        else:
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))

        # Add metadata
        if metadata:
            metadata_style = ParagraphStyle(
                'AuroraMetadata' if use_aurora_theme else 'Metadata',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#6b7280') if use_aurora_theme else colors.black,
                spaceAfter=4
            )
            for key, value in metadata.items():
                elements.append(Paragraph(f"<b>{key}:</b> {value}", metadata_style))
            elements.append(Spacer(1, 20))

        # Add timestamp
        timestamp = datetime.now().strftime("%d %B %Y at %H:%M")
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#9ca3af') if use_aurora_theme else colors.grey,
            fontName='Helvetica-Oblique'
        )
        elements.append(Paragraph(f"Generated: {timestamp}", timestamp_style))
        elements.append(Spacer(1, 24))

        # Convert DataFrame to table
        if not data.empty:
            # Prepare table data
            table_data = [data.columns.tolist()] + data.values.tolist()

            # Create table with Aurora or standard styling
            table = Table(table_data)

            if use_aurora_theme:
                # Aurora-themed table with purple/blue gradients
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),  # Purple header
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                    ('TOPPADDING', (0, 0), (-1, 0), 14),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),  # Light rows
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9fafb'), colors.HexColor('#f3f4f6')]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            else:
                # Original styling
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0077b6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))

            elements.append(table)
        else:
            elements.append(Paragraph("<i>No data available</i>", styles['Italic']))

        # Add footer with Aurora branding
        if use_aurora_theme:
            elements.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'AuroraFooter',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#9ca3af'),
                alignment=TA_CENTER
            )
            elements.append(Paragraph("Generated by UK Tax Helper - Aurora Edition", footer_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def export_to_json(self, data: pd.DataFrame, filename: str) -> bytes:
        """Export DataFrame to JSON format"""
        return data.to_json(orient='records', indent=2).encode('utf-8')

    def _generate_summary(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Generate summary sheet for Excel export"""
        summary_rows = []

        for sheet_name, df in data_dict.items():
            summary_rows.append({
                'Sheet Name': sheet_name,
                'Row Count': len(df),
                'Column Count': len(df.columns),
                'Columns': ', '.join(df.columns.tolist())
            })

        return pd.DataFrame(summary_rows)


def render_export_panel(session,
                        data: pd.DataFrame,
                        title: str,
                        filename_prefix: str,
                        metadata: Optional[Dict[str, str]] = None,
                        show_formats: List[str] = ['csv', 'excel', 'pdf', 'json'],
                        use_aurora_theme: bool = False):
    """
    Render export panel with download buttons for multiple formats

    Args:
        session: Database session
        data: DataFrame to export
        title: Title for the export
        filename_prefix: Prefix for downloaded files
        metadata: Optional metadata for PDF
        show_formats: List of formats to show ['csv', 'excel', 'pdf', 'json']
        use_aurora_theme: Whether to use Aurora-themed export panel
    """
    if use_aurora_theme:
        render_aurora_export_panel(session, data, title, filename_prefix, metadata, show_formats)
        return

    st.markdown("### 📥 Export Data")

    if data.empty:
        st.warning("No data available to export")
        return

    export_manager = ExportManager(session)

    # Create columns for export buttons
    cols = st.columns(len(show_formats))

    for idx, format_type in enumerate(show_formats):
        with cols[idx]:
            if format_type == 'csv':
                csv_data = export_manager.export_to_csv(data, f"{filename_prefix}.csv")
                st.download_button(
                    label="📄 CSV",
                    data=csv_data,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            elif format_type == 'excel':
                excel_data = export_manager.export_to_excel(
                    {title: data},
                    f"{filename_prefix}.xlsx"
                )
                st.download_button(
                    label="📊 Excel",
                    data=excel_data,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            elif format_type == 'pdf':
                if PDF_AVAILABLE:
                    pdf_data = export_manager.export_to_pdf(
                        data, title, f"{filename_prefix}.pdf", metadata
                    )
                    st.download_button(
                        label="📕 PDF",
                        data=pdf_data,
                        file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.button("📕 PDF", disabled=True, use_container_width=True,
                            help="Install reportlab to enable PDF export")

            elif format_type == 'json':
                json_data = export_manager.export_to_json(data, f"{filename_prefix}.json")
                st.download_button(
                    label="🔗 JSON",
                    data=json_data,
                    file_name=f"{filename_prefix}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )


def render_advanced_export_dialog(session,
                                  export_options: Dict[str, pd.DataFrame],
                                  title: str = "Export Data"):
    """
    Render advanced export dialog with multiple sheet selection

    Args:
        session: Database session
        export_options: Dictionary of {sheet_name: DataFrame}
        title: Dialog title
    """
    st.markdown(f"### {title}")

    # Sheet selection
    st.markdown("**Select sheets to include:**")
    selected_sheets = {}

    for sheet_name, df in export_options.items():
        if st.checkbox(f"{sheet_name} ({len(df)} rows)", value=True, key=f"export_{sheet_name}"):
            selected_sheets[sheet_name] = df

    if not selected_sheets:
        st.warning("Please select at least one sheet to export")
        return

    st.markdown("---")

    # Export format selection
    col1, col2 = st.columns(2)

    with col1:
        include_summary = st.checkbox("Include summary sheet", value=True)

    with col2:
        format_choice = st.selectbox(
            "Export format",
            options=['Excel (Multi-sheet)', 'CSV (Separate files)', 'PDF', 'JSON'],
            index=0
        )

    # Export button
    if st.button("📥 Export Selected Data", type="primary", use_container_width=True):
        export_manager = ExportManager(session)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format_choice == 'Excel (Multi-sheet)':
            excel_data = export_manager.export_to_excel(
                selected_sheets,
                f"tax_export_{timestamp}.xlsx",
                include_summary=include_summary
            )
            st.download_button(
                label="📊 Download Excel File",
                data=excel_data,
                file_name=f"tax_export_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.success(f"✅ Prepared {len(selected_sheets)} sheets for download")

        elif format_choice == 'CSV (Separate files)':
            st.info("Generating CSV files...")
            for sheet_name, df in selected_sheets.items():
                csv_data = export_manager.export_to_csv(df, f"{sheet_name}.csv")
                st.download_button(
                    label=f"📄 Download {sheet_name}.csv",
                    data=csv_data,
                    file_name=f"{sheet_name}_{timestamp}.csv",
                    mime="text/csv",
                    key=f"csv_{sheet_name}",
                    use_container_width=True
                )

        elif format_choice == 'PDF':
            if PDF_AVAILABLE:
                # Combine all sheets into one PDF
                combined_df = pd.concat(selected_sheets.values(), keys=selected_sheets.keys())
                pdf_data = export_manager.export_to_pdf(
                    combined_df.reset_index(drop=True),
                    "Tax Helper Export",
                    f"tax_export_{timestamp}.pdf",
                    metadata={
                        'Sheets Included': ', '.join(selected_sheets.keys()),
                        'Total Rows': str(sum(len(df) for df in selected_sheets.values()))
                    }
                )
                st.download_button(
                    label="📕 Download PDF",
                    data=pdf_data,
                    file_name=f"tax_export_{timestamp}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("PDF export requires reportlab. Install with: pip install reportlab")

        elif format_choice == 'JSON':
            # Export as single JSON with multiple keys
            json_export = {
                sheet_name: df.to_dict(orient='records')
                for sheet_name, df in selected_sheets.items()
            }
            json_data = json.dumps(json_export, indent=2).encode('utf-8')
            st.download_button(
                label="🔗 Download JSON",
                data=json_data,
                file_name=f"tax_export_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )


def render_aurora_export_panel(session,
                               data: pd.DataFrame,
                               title: str,
                               filename_prefix: str,
                               metadata: Optional[Dict[str, str]] = None,
                               show_formats: List[str] = ['csv', 'excel', 'pdf', 'json']):
    """
    Render Aurora-themed export panel with glassmorphic styling and gradient buttons

    Args:
        session: Database session
        data: DataFrame to export
        title: Title for the export
        filename_prefix: Prefix for downloaded files
        metadata: Optional metadata for PDF
        show_formats: List of formats to show
    """
    if data.empty:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">📭</div>
            <div style="font-size: 18px; font-weight: 500;">No data available to export</div>
        </div>
        """, unsafe_allow_html=True)
        return

    export_manager = ExportManager(session)
    timestamp = datetime.now().strftime('%Y%m%d')

    # Aurora-themed section header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4f8fea 0%, #3a6db8 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="-webkit-text-fill-color: initial; background: none;">💾</span>
        Export Your Data
    </div>
    """, unsafe_allow_html=True)

    # Aurora-themed glassmorphic container
    st.markdown("""
    <div style="
        background: rgba(21, 25, 52, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    ">
        <div style="
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            margin-bottom: 8px;
            font-weight: 600;
        ">
            📊 {title}
        </div>
        <div style="
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
        ">
            {row_count} rows available for export
        </div>
    </div>
    """.format(title=title, row_count=len(data)), unsafe_allow_html=True)

    # Create columns for export buttons
    cols = st.columns(len(show_formats))

    for idx, format_type in enumerate(show_formats):
        with cols[idx]:
            if format_type == 'csv':
                csv_data = export_manager.export_to_csv(data, f"{filename_prefix}.csv")

                # Aurora-styled download button
                st.markdown("""
                <style>
                .aurora-csv-btn button {
                    background: linear-gradient(135deg, #36c7a0 0%, #059669 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 12px !important;
                    padding: 12px 24px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 16px rgba(54, 199, 160, 0.3) !important;
                }
                .aurora-csv-btn button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 24px rgba(54, 199, 160, 0.5) !important;
                }
                </style>
                """, unsafe_allow_html=True)

                st.download_button(
                    label="📄 CSV",
                    data=csv_data,
                    file_name=f"{filename_prefix}_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key=f"aurora_csv_{filename_prefix}"
                )

            elif format_type == 'excel':
                excel_data = export_manager.export_to_excel(
                    {title: data},
                    f"{filename_prefix}.xlsx"
                )

                st.markdown("""
                <style>
                .aurora-excel-btn button {
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 12px !important;
                    padding: 12px 24px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3) !important;
                }
                .aurora-excel-btn button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 24px rgba(59, 130, 246, 0.5) !important;
                }
                </style>
                """, unsafe_allow_html=True)

                st.download_button(
                    label="📊 Excel",
                    data=excel_data,
                    file_name=f"{filename_prefix}_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"aurora_excel_{filename_prefix}"
                )

            elif format_type == 'pdf':
                if PDF_AVAILABLE:
                    pdf_data = export_manager.export_to_pdf(
                        data, title, f"{filename_prefix}.pdf", metadata
                    )

                    st.markdown("""
                    <style>
                    .aurora-pdf-btn button {
                        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
                        color: white !important;
                        border: none !important;
                        border-radius: 12px !important;
                        padding: 12px 24px !important;
                        font-weight: 600 !important;
                        transition: all 0.3s ease !important;
                        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3) !important;
                    }
                    .aurora-pdf-btn button:hover {
                        transform: translateY(-2px) !important;
                        box-shadow: 0 6px 24px rgba(139, 92, 246, 0.5) !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    st.download_button(
                        label="📕 PDF",
                        data=pdf_data,
                        file_name=f"{filename_prefix}_{timestamp}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"aurora_pdf_{filename_prefix}"
                    )
                else:
                    st.markdown("""
                    <div style="
                        background: rgba(107, 114, 128, 0.2);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 12px;
                        padding: 12px 24px;
                        text-align: center;
                        color: rgba(255, 255, 255, 0.4);
                        font-weight: 600;
                        cursor: not-allowed;
                    ">
                        📕 PDF (Install reportlab)
                    </div>
                    """, unsafe_allow_html=True)

            elif format_type == 'json':
                json_data = export_manager.export_to_json(data, f"{filename_prefix}.json")

                st.markdown("""
                <style>
                .aurora-json-btn button {
                    background: linear-gradient(135deg, #ec4899 0%, #db2777 100%) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 12px !important;
                    padding: 12px 24px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.3) !important;
                }
                .aurora-json-btn button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 24px rgba(236, 72, 153, 0.5) !important;
                }
                </style>
                """, unsafe_allow_html=True)

                st.download_button(
                    label="🔗 JSON",
                    data=json_data,
                    file_name=f"{filename_prefix}_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True,
                    key=f"aurora_json_{filename_prefix}"
                )

    # Aurora-themed info footer
    st.markdown("""
    <div style="
        margin-top: 20px;
        padding: 16px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
        border-left: 3px solid rgba(139, 92, 246, 0.5);
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
    ">
        <strong style="color: rgba(255, 255, 255, 0.9);">✨ Export Tips:</strong><br>
        • CSV - Best for spreadsheet software and data analysis<br>
        • Excel - Professional multi-sheet reports with formatting<br>
        • PDF - Beautiful print-ready documents<br>
        • JSON - Perfect for data integration and APIs
    </div>
    """, unsafe_allow_html=True)
