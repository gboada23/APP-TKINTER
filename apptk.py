import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
from conexionsql import SQLSERVER, MYSQL
from pdf import PDFGenerator  # Importar la clase PDFGenerator

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Negociaciones")
        self.geometry("1400x850")
        self.iconbitmap("logo.ico")
        # Inicializar conexiones
        self.mysql = MYSQL()
        self.sqlserver_manager = SQLSERVER()
        self.baremos = self.mysql.tabla_baremos()
        self.products = []
        self.comedores = pd.read_excel(r"archivos/comedores.xlsx")

        # Variables de control
        self.control_number = tk.StringVar()
        self.comedor = tk.StringVar()
        self.npedido = tk.StringVar()
        self.familiainicial = tk.StringVar()
        self.codinicial = tk.StringVar()
        self.nominicial = tk.StringVar()
        self.unidadinicial = tk.StringVar()
        self.solicitadoinicial = tk.IntVar()
        self.costodolarinicial = tk.DoubleVar()
        self.preciodolarinicial = tk.DoubleVar()
        self.preciototalinicial = tk.DoubleVar()

        self.familianeg = tk.StringVar()
        self.codneg = tk.StringVar()
        self.nomneg = tk.StringVar()
        self.unidadneg = tk.StringVar()
        self.solicitadoneg = tk.IntVar()
        self.costodolarneg = tk.DoubleVar()
        self.preciodolarneg = tk.DoubleVar()
        self.preciototalneg = tk.DoubleVar()
        self.cantidad_sugerida = tk.IntVar()

        self.monto_faltante = tk.DoubleVar(value=0.0)
        self.monto_faltante_actual = tk.DoubleVar(value=0.0)
        self.facturado_procesado = False
        self.total_enviado = tk.DoubleVar(value=0.0)

        # Variables para la gestión de checkboxes
        self.checkbox_vars = []

        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Encabezado
        tk.Label(scrollable_frame, text="Gestión de Negociaciones", font=("Helvetica", 14, "bold"), bg="#0C4B85", fg="white").pack(fill=tk.X)
        header_frame = tk.Frame(scrollable_frame, bg="#0C4B85")
        header_frame.pack(fill=tk.X)

        # Reducir el tamaño del logo a la mitad
        logo_image = tk.PhotoImage(file="logos/logotrans.png").subsample(4, 4)
        tk.Label(header_frame, image=logo_image, bg="#0C4B85").pack(side=tk.LEFT, padx=5)

        # Número de control
        tk.Label(header_frame, text="Número de Control:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Entry(header_frame, textvariable=self.control_number, font=("Helvetica", 8), width=12).pack(side=tk.LEFT, padx=5)

        # Número de pedido
        tk.Label(header_frame, text="Número de Pedido:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Entry(header_frame, textvariable=self.npedido, font=("Helvetica", 8), width=12).pack(side=tk.LEFT, padx=5)

        # Comedor
        tk.Label(header_frame, text="Comedor:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").pack(side=tk.LEFT, padx=5)
        comedor_menu = ttk.Combobox(header_frame, textvariable=self.comedor, font=("Helvetica", 8), values=self.comedores['comedor'].sort_values().tolist(), width=45)
        comedor_menu.pack(side=tk.LEFT, padx=5)
        comedor_menu.bind("<<ComboboxSelected>>", self.update_product_options)

        # Botón de generar PDF en el encabezado
        self.pdf_generator = PDFGenerator(header_frame, self.sqlserver_manager, bg="#0C4B85")
        self.pdf_generator.pack(side=tk.RIGHT, padx=5)

        # Sección de Productos
        product_frame = tk.Frame(scrollable_frame)
        product_frame.pack(fill=tk.X, pady=2)

        self.create_product_frame(product_frame, "Producto Facturado",
                                  self.familiainicial, self.nominicial, self.codinicial,
                                  self.unidadinicial, self.solicitadoinicial, self.costodolarinicial,
                                  self.preciodolarinicial, self.preciototalinicial, filter_by_comedor=True)

        self.create_product_frame(product_frame, "Producto a Enviar",
                                  self.familianeg, self.nomneg, self.codneg,
                                  self.unidadneg, self.solicitadoneg, self.costodolarneg,
                                  self.preciodolarneg, self.preciototalneg,
                                  filter_by_comedor=False, is_negotiated=True)

        # Botón de agregar producto
        action_frame = tk.Frame(scrollable_frame, bg="#F0F0F0")
        action_frame.pack(fill=tk.X, pady=5)

        tk.Label(action_frame, text="Monto Faltante $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(side=tk.LEFT, padx=5)
        tk.Label(action_frame, textvariable=self.monto_faltante, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(side=tk.LEFT)

        tk.Button(action_frame, text="Agregar Producto", command=self.add_product, bg="#0C4B85", fg="white", font=("Helvetica", 8)).pack(side=tk.RIGHT, padx=5)

        # Tabla de productos agregados
        columns = ("Codigo Zudalpro", "Producto a Enviar", "Unidad de medida", "Cantidad a Enviar", "Precio Total $", "Eliminar")
        self.tree = ttk.Treeview(scrollable_frame, columns=columns, show="headings", height=3)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, pady=2)

        # Botón de eliminar productos seleccionados
        self.delete_button = tk.Button(scrollable_frame, text="Eliminar Productos Seleccionados", command=self.delete_selected_products, bg="#FF6347", fg="white", font=("Helvetica", 8, "bold"))
        self.delete_button.pack(side=tk.RIGHT, padx=5)

        # Mostrar Total Enviado
        tk.Label(scrollable_frame, text="Total Enviado $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(side=tk.LEFT, pady=2)
        tk.Label(scrollable_frame, textvariable=self.total_enviado, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(side=tk.LEFT, pady=2)

        # Botón de enviar negociación a la base de datos
        self.submit_button = tk.Button(scrollable_frame, text="Generar negociación", command=self.submit_negociacion, bg="#0C4B85", fg="white", font=("Helvetica", 9, "bold"))
        self.submit_button.pack(pady=5)

        # Necesario para que la imagen del logo se mantenga
        self.logo_image = logo_image

    def create_product_frame(self, parent, title, familia_var, nombre_var, codigo_var, unidad_var, cantidad_var, costo_var, precio_var, precio_total_var, filter_by_comedor=False, is_negotiated=False):
        frame = tk.LabelFrame(parent, text=title, font=("Helvetica", 8, "bold"), padx=5, pady=5, bg="#F0F0F0")
        frame.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Familia:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        tk.Label(frame, textvariable=familia_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        tk.Label(frame, text="Descripción del Producto:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        product_menu = ttk.Combobox(frame, textvariable=nombre_var, font=("Helvetica", 8), width=20)
        product_menu.pack(fill=tk.X, padx=2)
        product_menu.bind("<<ComboboxSelected>>", lambda _: self.update_product_info(nombre_var, codigo_var, familia_var, unidad_var))

        if filter_by_comedor:
            self.product_menu_inicial = product_menu
        else:
            product_menu['values'] = self.baremos['descripcion_zudalpro'].sort_values().unique().tolist()

        tk.Label(frame, text="Código del Producto:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        tk.Label(frame, textvariable=codigo_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        tk.Label(frame, text="Unidad de Medida:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        self.unidad_menu = ttk.Combobox(frame, textvariable=unidad_var, font=("Helvetica", 8), width=20)
        self.unidad_menu.pack(fill=tk.X, padx=2)

        tk.Label(frame, text="Cantidad:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        cantidad_entry = tk.Entry(frame, textvariable=cantidad_var, font=("Helvetica", 8), width=10)
        cantidad_entry.pack(padx=2)
        cantidad_entry.bind("<KeyRelease>", lambda _: self.calculate_price_total(cantidad_var, precio_var, precio_total_var, is_negotiated))

        tk.Label(frame, text="Costo Unitario $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        cost_entry = tk.Entry(frame, textvariable=costo_var, font=("Helvetica", 8), width=10)
        cost_entry.pack(padx=2)
        cost_entry.bind("<KeyRelease>", lambda _: self.calculate_price_total(cantidad_var, precio_var, precio_total_var, is_negotiated))

        tk.Label(frame, text="Precio Unitario $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        if is_negotiated:
            tk.Label(frame, textvariable=precio_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")
        else:
            precio_entry = tk.Entry(frame, textvariable=precio_var, font=("Helvetica", 8), width=10)
            precio_entry.pack(padx=2)
            precio_entry.bind("<KeyRelease>", lambda _: self.calculate_price_total(cantidad_var, precio_var, precio_total_var, is_negotiated))

        tk.Label(frame, text="Precio Total $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        tk.Label(frame, textvariable=precio_total_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        if is_negotiated:
            tk.Label(frame, text="Cantidad Sugerida:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
            tk.Label(frame, textvariable=self.cantidad_sugerida, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(pady=2, anchor="w")

    def calculate_price_total(self, cantidad_var, precio_var, precio_total_var, is_negotiated):
        try:
            cantidad = cantidad_var.get()
            costo_unitario = self.costodolarneg.get()

            if is_negotiated:
                if costo_unitario:
                    self.preciodolarneg.set(round(costo_unitario / 0.65, 2))

                precio_unitario = self.preciodolarneg.get()
            else:
                precio_unitario = precio_var.get()

            if cantidad == '':
                cantidad = 0
            if precio_unitario == '':
                precio_unitario = 0

            total = round(float(cantidad) * float(precio_unitario), 2)
            precio_total_var.set(total)

            if is_negotiated:
                if self.monto_faltante_actual.get() > 0 and precio_unitario > 0:
                    cantidad_sugerida = self.monto_faltante_actual.get() / precio_unitario
                    self.cantidad_sugerida.set(int(cantidad_sugerida))
                else:
                    self.cantidad_sugerida.set(0)

        except Exception as e:
            print(f"Error al calcular el precio total: {e}")

    def update_product_options(self, _):
        comedor = self.comedor.get()
        filtered_unidades = self.baremos[self.baremos['comedor'] == comedor]['descripcion_zudalpro'].sort_values().unique().tolist()
        self.product_menu_inicial['values'] = filtered_unidades

    def update_product_info(self, nombre_var, codigo_var, familia_var, unidad_var):
        nombre_producto = nombre_var.get()
        filtered_data = self.baremos[self.baremos['descripcion_zudalpro'] == nombre_producto]
        if not filtered_data.empty:
            codigo_var.set(filtered_data['codzudalpro'].values[0].strip())
            familia_var.set(filtered_data['familia'].values[0].strip())
            presentaciones = filtered_data['presentacion'].sort_values().unique().tolist()
            self.unidad_menu['values'] = presentaciones
            unidad_var.set(presentaciones[0].strip() if presentaciones else '')

            # Si el producto facturado cambia, actualizar el monto faltante
            if nombre_var == self.nominicial:
                solicitadoinicial = self.solicitadoinicial.get()
                preciodolarinicial = self.preciodolarinicial.get()
                preciototaldolarinicial = solicitadoinicial * preciodolarinicial

                # Actualizar el monto faltante y el precio total inicial
                self.preciototalinicial.set(preciototaldolarinicial)
                self.monto_faltante_actual.set(preciototaldolarinicial)
                self.monto_faltante.set(round(self.monto_faltante_actual.get(), 2))
                self.total_enviado.set(0.0)  # Reiniciar el total enviado
                self.facturado_procesado = True
                messagebox.showinfo("Producto Facturado Cambiado", "Se ha actualizado el monto faltante según el nuevo producto facturado.")

    def add_product(self):
        cantidad_enviada = self.solicitadoneg.get()
        precio_unitario_enviado = self.preciodolarneg.get()
        precio_total_enviado = cantidad_enviada * precio_unitario_enviado

        # Actualizar el total enviado con redondeo
        self.total_enviado.set(round(self.total_enviado.get() + precio_total_enviado, 2))

        # Calcular y actualizar el monto faltante con redondeo
        self.monto_faltante_actual.set(round(self.preciototalinicial.get() - self.total_enviado.get(), 2))
        self.monto_faltante.set(self.monto_faltante_actual.get())

        # Si el monto faltante es menor o igual a 0, notificamos al usuario
        if self.monto_faltante_actual.get() <= 0:
            messagebox.showinfo("Monto Cubierto", "El monto del producto facturado ha sido cubierto.")
            self.monto_faltante_actual.set(0)
            self.monto_faltante.set(0)

        data = {
            'codclie': self.control_number.get().strip(),
            'fechaneg': datetime.today().strftime('%Y-%m-%d'),
            'comedor': self.comedor.get().strip(),
            'npedido': self.npedido.get().strip(),
            'familiainicial': self.familiainicial.get().strip(),
            'codinicial': self.codinicial.get().strip(),
            'nominicial': self.nominicial.get().strip(),
            'undinicial': self.unidadinicial.get().strip(),
            'solicitadoinicial': self.solicitadoinicial.get(),
            'costodolarinicial': self.costodolarinicial.get(),
            'preciodolarinicial': self.preciodolarinicial.get(),
            'familianeg': self.familianeg.get().strip(),
            'codneg': self.codneg.get().strip(),
            'nomneg': self.nomneg.get().strip(),
            'undneg': self.unidadneg.get().strip(),
            'solicitadoneg': self.solicitadoneg.get(),
            'costodolarneg': self.costodolarneg.get(),
            'preciodolarneg': self.preciodolarneg.get(),
            'precio_total_neg': precio_total_enviado
        }

        self.products.append(data)
        self.update_table()
        self.calculate_price_total(self.solicitadoneg, self.preciodolarneg, self.preciototalneg, True)

    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for product in self.products:
            self.tree.insert("", tk.END, values=(
                product['codneg'].strip(),
                product['nomneg'].strip(),
                product['undneg'].strip(),
                product['solicitadoneg'],
                product['precio_total_neg'],
            ))


    def delete_selected_products(self):
        selected_items = self.tree.selection()

        if selected_items:
            for item in selected_items:
                item_index = self.tree.index(item)
                product = self.products[item_index]

                # Restar el monto eliminado del total enviado con redondeo
                self.total_enviado.set(round(self.total_enviado.get() - product['precio_total_neg'], 2))

                # Actualizar el monto faltante con redondeo
                self.monto_faltante_actual.set(round(self.preciototalinicial.get() - self.total_enviado.get(), 2))
                self.monto_faltante.set(self.monto_faltante_actual.get())

                # Eliminar el producto de la lista
                del self.products[item_index]

            self.update_table()

            messagebox.showinfo("Productos Eliminados", "Los productos seleccionados han sido eliminados correctamente.")
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona al menos un producto para eliminar.")

    def submit_negociacion(self):
        try:
            for product in self.products:
                product['codclie'] = product['codclie'].strip()
                product['comedor'] = product['comedor'].strip()
                product['npedido'] = product['npedido'].strip()
                product['familiainicial'] = product['familiainicial'].strip()
                product['codinicial'] = product['codinicial'].strip()
                product['nominicial'] = product['nominicial'].strip()
                product['undinicial'] = product['undinicial'].strip()
                product['familianeg'] = product['familianeg'].strip()
                product['codneg'] = product['codneg'].strip()
                product['nomneg'] = product['nomneg'].strip()
                product['undneg'] = product['undneg'].strip()

            df = pd.DataFrame(self.products)

            df['preciototaldolarneg'] = df['solicitadoneg'] * df['preciodolarneg']

            if 'precio_total_neg' in df.columns:
                df = df.drop(columns=['precio_total_neg'])

            df['costototaldolarinicial'] = df['solicitadoinicial'] * df['costodolarinicial']
            df['preciototaldolarinicial'] = df['solicitadoinicial'] * df['preciodolarinicial']
            df['rentabilidadinicial'] = ((df['preciodolarinicial'] - df['costodolarinicial']) / df['preciodolarinicial']) * 100
            df['utilidadinicial'] = df['preciototaldolarinicial'] - df['costototaldolarinicial']
            df['costototaldolarneg'] = df['solicitadoneg'] * df['costodolarneg']
            df['rentabilidadneg'] = ((df['preciodolarneg'] - df['costodolarneg']) / df['preciodolarneg']) * 100
            df['utilidadneg'] = df['preciototaldolarneg'] - df['costototaldolarneg']
        # Intentar agregar los datos a la base de datos y capturar el resultado
            result_message = self.sqlserver_manager.add_data('NEGOCIACIONDAT', df)
            
            if "exitosamente" in result_message:
                # Si se agregó con éxito, limpiar la interfaz y mostrar el mensaje
                messagebox.showinfo("Éxito", result_message)
                self.products = []
                self.update_table()
                self.preciototalinicial.set(0.0)
                self.monto_faltante.set(0.0)
                self.monto_faltante_actual.set(0.0)
                self.total_enviado.set(0.0)
                self.facturado_procesado = False
            else:
                # Si hubo un error, mostrar el mensaje de error
                messagebox.showerror("Error", result_message)

        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error inesperado: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()


