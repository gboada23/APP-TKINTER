import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from conexionsql import SQLSERVER
from datetime import datetime


class PDFGenerator(tk.Frame):
    def __init__(self, parent, sqlserver_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.sqlserver_manager = sqlserver_manager
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Numero de control:", bg="#0C4B85",fg="white",font=("Helvetica", 10,"bold")).grid(row=0, column=0, pady=5, sticky="e")
        self.codclie_entry = tk.Entry(self, font=("Helvetica", 10), width=12)
        self.codclie_entry.grid(row=0, column=1, pady=5, padx=5)
        
        self.generate_button = tk.Button(self, text="Generar PDF", command=self.generate_pdf, bg="#0C4B85", fg="white", font=("Helvetica", 10))
        self.generate_button.grid(row=1, column=0, columnspan=2, pady=10)

    def generate_pdf(self):
        codclie = self.codclie_entry.get().strip()

        if codclie:
            data = self.sqlserver_manager.filtro_codclie(codclie)
            data = data.drop('cantreal',axis=1)
            if data is not None and not data.empty:
                comedor = data['comedor'].iloc[0] if 'comedor' in data.columns else 'N/A'
                fechaneg = data['fechaneg'].iloc[0] if 'fechaneg' in data.columns else 'N/A'
                npedido = data['npedido'].iloc[0] if 'npedido' in data.columns else 'N/A'
                familiainicial = data['familiainicial'].iloc[0] if 'familiainicial' in data.columns else 'N/A'
                familianeg = data['familianeg'].iloc[0] if 'familianeg' in data.columns else 'N/A'

                filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"{codclie}.pdf")
                if filename:
                    self.create_pdf(data, filename, codclie, fechaneg, npedido, comedor, familiainicial, familianeg)
                    messagebox.showinfo("Éxito", f"PDF generado exitosamente: {filename}")
            else:
                messagebox.showerror("Error", "No se encontraron datos para el Numero de control proporcionado.")
        else:
            messagebox.showwarning("Numero de control en blanco", "Por favor, introduce un código de cliente.")

    def create_pdf(self, data, filename, codclie, fechaneg, npedido, comedor, familiainicial, familianeg):
        c = canvas.Canvas(filename, pagesize=landscape(letter))
        width, height = landscape(letter)

        def draw_header():
            c.drawInlineImage('logos/logo.png', 70, height - 60, width=180, height=60)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 100, f"REPORTE DE NEGOCIACIONES")
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.red)
            c.drawString(width - 290, height - 20, f"NUMERO DE CONTROL: {codclie}")
            c.setFillColor(colors.black)
            c.drawString(70, height - 80, f"FECHA: {datetime.now().strftime('%d/%m/%Y')}")
            c.drawString(width - 290, height - 40, f"NUMERO DE PEDIDO ASOCIADO: {npedido}")
            c.setFont("Helvetica", 7)
            c.drawString(width - 290, height - 60, f"SEDE: {comedor}")
            c.setFont("Helvetica", 7)

        def draw_table1():
            # Dibujar el "header" general para la tabla 1
            box_x = 1 * inch
            box_y = 5.9 * inch  # Ajusta la altura para que esté justo arriba del header de la tabla
            box_width = sum(col_widths)  # Ancho total de la tabla
            box_height = 0.3 * inch  # Alto del rectángulo

            # Dibujar el rectángulo
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.lightgrey)
            c.rect(box_x, box_y, box_width, box_height, fill=1)

            # Agregar el texto dentro del rectángulo
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(box_x + box_width / 2, box_y + box_height / 2 - 3, "Producto Facturado")

            # Ahora dibujar la tabla 1 justo debajo del nuevo "header"
            table1.wrapOn(c, c._pagesize[0] - 2 * inch, c._pagesize[1] - 4 * inch)
            table1.drawOn(c, 1 * inch, 5 * inch)
            draw_responsable_boxes() # Llama a la función draw_responsable_boxes() en la posición correcta de tu código para que ambos cuadros se dibujen.

        def draw_table2():
        # Dibujar el "header" general para la tabla 2
            box_x = 1 * inch
            box_y = 6.4* inch  # Ajusta la altura para que esté justo arriba del header de la tabla
            box_width = sum(col_widths)  # Ancho total de la tabla
            box_height = 0.3 * inch  # Alto del rectángulo

            # Dibujar el rectángulo
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.lightgrey)
            c.rect(box_x, box_y, box_width, box_height, fill=1)

            # Agregar el texto dentro del rectángulo
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(box_x + box_width / 2, box_y + box_height / 2 - 3, "Producto Enviado")
            table2.wrapOn(c, c._pagesize[0] - 2 * inch, c._pagesize[1] - 4 * inch)
            table2.drawOn(c, 1 * inch, 5.5 * inch)
        def draw_summary_box():
            # Dimensiones y posición del cuadro
            box_x = 550
            box_y = height - 150  # Ajustar la altura para incluir todos los textos
            box_width = 195
            box_height = 50 if resultado > 0 else 30  # Ajustar la altura según la cantidad de líneas

            # Dibuja el rectángulo de fondo
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.lightblue)
            c.rect(box_x, box_y, box_width, box_height, fill=1)

            # Dibuja los textos dentro del cuadro según la condición
            if resultado > 0:
                c.setFillColor(colors.black)
                c.drawString(box_x + 10, box_y + box_height - 10, f"Resultado negociacion {round(resultado, 2)}$")
                c.drawString(box_x + 10, box_y + box_height - 25, f"Utlidad Bruta {round(utilidad_general, 2)}$")
                c.drawString(box_x + 10, box_y + box_height - 40, f"Rentabilidad {round(rentabilidad_general * 100, 2)}%")
            else:
                c.setFillColor(colors.red)
                c.drawString(box_x + 10, box_y + box_height - 10, f"Negociacion en contra por {round(resultado, 2)}$")

        def draw_responsable_boxes():
    # Posiciones y dimensiones del primer cuadro
            box_x = 1 * inch
            box_y = 0.6 * inch  # Bajamos el cuadro más hacia el fondo de la página
            box_width = 3.5 * inch
            box_height = 1.3 * inch

            # Cuadro de RESPONSABLE DE ZUDALPRO
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.lightblue)
            c.rect(box_x, box_y, box_width, box_height, fill=1)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(box_x + box_width / 2, box_y + box_height - 15, "RESPONSABLE DE ZUDALPRO")

            c.setFont("Helvetica", 8)
            c.drawCentredString(box_x + box_width / 2, box_y + box_height - 35, "MARIELA GUTIERREZ")

            c.drawString(box_x + box_width / 2 - 20, box_y + box_height - 50, "Firma")
            c.drawString(box_x + box_width - 90,box_y + box_height - 90, f"{datetime.now().strftime('%d/%m/%Y')}")

            # Dibuja la línea para la firma centrada
            c.setStrokeColor(colors.black)
            c.line(box_x + 70, box_y + box_height - 65, box_x + 190, box_y + box_height - 65)

            # Posiciones y dimensiones del segundo cuadro paralelo
            box_x_right = width - (box_width + 0.65 * inch)
            box_y_right = box_y  # Mantener la misma altura para que quede paralelo

            # Cuadro de RESPONSABLE POR CLIENTE
            c.setStrokeColor(colors.black)
            c.setFillColor(colors.lightblue)
            c.rect(box_x_right, box_y_right, box_width, box_height, fill=1)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(box_x_right + box_width / 2, box_y_right + box_height - 15, "RESPONSABLE POR CLIENTE")

            c.setFont("Helvetica", 8)
            c.drawCentredString(box_x_right + 50, box_y_right + box_height - 35, "NOMBRE DEL CLIENTE:")

            c.drawString(box_x_right + box_width / 2 - 20, box_y_right + box_height - 50, "Firma")
            c.drawString(box_x_right + box_width - 90, box_y_right + box_height - 90, f"{datetime.now().strftime('%d/%m/%Y')}")

            # Dibuja la línea para la firma centrada
            c.setStrokeColor(colors.black)
            c.line(box_x_right + 70, box_y_right + box_height - 65, box_x_right + 190, box_y_right + box_height - 65)

            # OBSERVACIONES
            c.setFont("Helvetica-Bold", 9)
            c.drawString(box_x, box_y + box_height - 110, "OBSERVACIÓN: Los productos negociados no afectan la facturación.")


        data = data.drop(columns=['comedor', 'codclie', 'fechaneg', 'npedido', 'familiainicial', 'familianeg'])
        data1 = data.iloc[:, :10]
        data2 = data.iloc[:, 10:]
        
        # Obtener productos únicos en 'data1' basado en la columna de descripción del producto
        data1 = data1.drop_duplicates(subset=['nominicial'])
        data2 = data2.drop_duplicates(subset=['nomneg'])

        # Renombrar columnas como se hacía antes
        renombre = {
            'codinicial':'COD', 'nominicial':'DESCRIPCION \nDEL PRODUCTO', 'undinicial':'UNIDAD \nDE MEDIDA',
            'solicitadoinicial':'CANTIDAD\nSOLICITADA', 'costodolarinicial':'COSTO \n UNITARIO $',
            'costototaldolarinicial':'COSTO \n TOTAL $', 'preciodolarinicial':'PRECIO \n UNITARIO $',
            'preciototaldolarinicial': 'PRECIO \n TOTAL $', 'rentabilidadinicial':'RENTABILIDAD \n %', 'utilidadinicial':'UTILIDAD \n BRUTA'
        }
        renombre2 = {
            'codneg':'COD', 'nomneg':'DESCRIPCION \nDEL PRODUCTO', 'undneg':'UNIDAD \nDE MEDIDA',
            'solicitadoneg':'CANTIDAD\nSOLICITADA', 'costodolarneg':'COSTO \n UNITARIO $',
            'costototaldolarneg':'COSTO \n TOTAL $', 'preciodolarneg':'PRECIO \n UNITARIO $',
            'preciototaldolarneg':'PRECIO \n TOTAL $', 'rentabilidadneg':'RENTABILIDAD \n %', 'utilidadneg':'UTILIDAD \n BRUTA'
        }

        data1.rename(columns=renombre, inplace=True)
        data2.rename(columns=renombre2, inplace=True)

        col_tex = ['COD','DESCRIPCION \nDEL PRODUCTO','UNIDAD \nDE MEDIDA']
        for col in col_tex:
            data1[col] = data1[col].str.strip()
            data2[col] = data2[col].str.strip()

        def format_percentage(x):
            return f"{x:.2f} %"

        def format_dolar(x):
            return f"{x:.2f} $"

        data1['CANTIDAD\nSOLICITADA'] = pd.to_numeric(data1['CANTIDAD\nSOLICITADA'], errors='coerce')
        data1['COSTO \n TOTAL $'] = pd.to_numeric(data1['COSTO \n TOTAL $'], errors='coerce')
        data1['PRECIO \n TOTAL $'] = pd.to_numeric(data1['PRECIO \n TOTAL $'], errors='coerce')
        data1['UTILIDAD \n BRUTA'] = pd.to_numeric(data1['UTILIDAD \n BRUTA'], errors='coerce')
        data1['RENTABILIDAD \n %'] = pd.to_numeric(data1['RENTABILIDAD \n %'],errors='coerce')
        data2['CANTIDAD\nSOLICITADA'] = pd.to_numeric(data2['CANTIDAD\nSOLICITADA'], errors='coerce')
        data2['COSTO \n TOTAL $'] = pd.to_numeric(data2['COSTO \n TOTAL $'], errors='coerce')
        data2['PRECIO \n TOTAL $'] = pd.to_numeric(data2['PRECIO \n TOTAL $'], errors='coerce')
        data2['UTILIDAD \n BRUTA'] = pd.to_numeric(data2['UTILIDAD \n BRUTA'], errors='coerce')

        total_solicitado1 = data1['CANTIDAD\nSOLICITADA'].sum()
        total_costototal1 = data1['COSTO \n TOTAL $'].sum()
        total_preciototal1 = data1['PRECIO \n TOTAL $'].sum()
        total_utilidad1 = data1['UTILIDAD \n BRUTA'].sum()
        avg_rentabilidad1 = data1['RENTABILIDAD \n %'].mean()

        total_solicitado2 = data2['CANTIDAD\nSOLICITADA'].sum()
        total_costototal2 = data2['COSTO \n TOTAL $'].sum()
        total_preciototal2 = data2['PRECIO \n TOTAL $'].sum()
        total_utilidad2 = data2['UTILIDAD \n BRUTA'].sum()
        avg_rentabilidad2 = data2['RENTABILIDAD \n %'].mean()
        resultado = total_utilidad2 - total_utilidad1
        utilidad_general = total_preciototal1 - total_costototal2
        rentabilidad_general = utilidad_general/total_preciototal1
        data1['RENTABILIDAD \n %'] = data1['RENTABILIDAD \n %'].apply(format_percentage)
        data2['RENTABILIDAD \n %'] = data2['RENTABILIDAD \n %'].apply(format_percentage)
        columnas = ['COSTO \n UNITARIO $','COSTO \n TOTAL $','PRECIO \n UNITARIO $','PRECIO \n TOTAL $','UTILIDAD \n BRUTA']
        for columna in columnas:
            data1[columna] = data1[columna].apply(format_dolar)
            data2[columna] = data2[columna].apply(format_dolar)

        total_row1 = [''] + ['TOTAL FACTURADO'] + [''] + [f"{total_solicitado1:.2f}", '', f"{total_costototal1:.2f} $", '', f"{total_preciototal1:.2f} $", f"{avg_rentabilidad1:.2f}%", f"{total_utilidad1:.2f} $"]
        total_row2 = [''] + ['TOTAL ENVIADO'] + [''] + [f"{total_solicitado2:.2f}", '', f"{total_costototal2:.2f} $", '', f"{total_preciototal2:.2f} $", f"{avg_rentabilidad2:.2f}%", f"{total_utilidad2:.2f} $"]
        data_list1 = [data1.columns.tolist()] + data1.values.tolist() + [total_row1]
        data_list2 = [data2.columns.tolist()] + data2.values.tolist() + [total_row2]

        col_widths = [0.68 * inch, 2.7 * inch, 1.4 * inch, 0.65 * inch, 0.65 * inch, 0.65 * inch, 0.65 * inch, 0.65 * inch, 0.70 * inch, 0.65 * inch]

        table1 = Table(data_list1, colWidths=col_widths)
        table2 = Table(data_list2, colWidths=col_widths)

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),  
            ('TOPPADDING', (0, 0), (-1, 0), 4),     
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow), 
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
        table1.setStyle(style)

        style2 = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.deepskyblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, -1), (-1, -1), colors.yellow), 
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ])
        table2.setStyle(style2)

        draw_header()
        draw_table1()
        c.setFont("Helvetica-Bold", 10)
        draw_summary_box()

        c.showPage()

        draw_header()
        draw_table2()



        c.save()
