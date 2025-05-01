from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

# Конфигурация стилей
def configure_styles():
    styles = getSampleStyleSheet()
    
    # Кастомный стиль для заголовка
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=14,
        alignment=1  # Центральное выравнивание
    ))
    
    # Стиль для заголовков таблицы
    table_header_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ])
    
    # Основной стиль таблицы
    table_body_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    
    return styles, table_header_style, table_body_style

def generate_report(data):
    if not data:
        raise ValueError("No data available for report generation")
    
    # Инициализация стилей
    styles, header_style, body_style = configure_styles()
    
    # Создание документа
    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    # Добавление заголовка
    elements.append(Paragraph("Horse Detection Report", styles['ReportTitle']))
    
    # Подготовка данных таблицы
    table_data = [
        ["Timestamp", "Filename", "Horse Count"],
        *[[
            row['timestamp'],
            row['filename'],
            str(row['horse_count'])
        ] for row in data]
    ]
    
    # Создание и настройка таблицы
    table = Table(
        table_data,
        colWidths=[120, 200, 80],  # Оптимальные ширины столбцов
        repeatRows=1  # Повторять заголовок на каждой странице
    )
    
    # Применение стилей
    table.setStyle(header_style)
    table.setStyle(body_style)
    
    elements.append(table)
    
    # Генерация PDF
    doc.build(elements)
    return filename