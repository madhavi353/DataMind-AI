
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_pdf_report(df, insights):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()
    elements = []

    # Report title
    elements.append(
        Paragraph("DataMind AI - Analytics Report", styles["Title"])
    )
    elements.append(Spacer(1, 20))

    # Dataset information
    elements.append(
        Paragraph("Dataset Overview", styles["Heading2"])
    )

    overview = [
        ["Metric", "Value"],
        ["Total Rows", str(df.shape[0])],
        ["Total Columns", str(df.shape[1])],
        ["Missing Values", str(df.isnull().sum().sum())],
        ["Duplicate Rows", str(df.duplicated().sum())]
    ]

    table = Table(overview, colWidths=[220, 150])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Column information
    elements.append(
        Paragraph("Column Information", styles["Heading2"])
    )

    column_data = [["Column Name", "Data Type", "Missing Values"]]

    for column in df.columns:
        column_data.append([
            str(column),
            str(df[column].dtype),
            str(df[column].isnull().sum())
        ])

    column_table = Table(column_data, repeatRows=1)

    column_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(column_table)
    elements.append(Spacer(1, 20))

    # Statistical summary
    elements.append(
        Paragraph("Statistical Summary", styles["Heading2"])
    )

    summary = df.describe(include="all").fillna("-").astype(str)

    summary_data = [
        ["Statistic"] + [str(col) for col in summary.columns]
    ]

    for index, row in summary.iterrows():
        summary_data.append([str(index)] + row.tolist())

    summary_table = Table(summary_data, repeatRows=1)

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(summary_table)

    document.build(elements)

    buffer.seek(0)
    return buffer
