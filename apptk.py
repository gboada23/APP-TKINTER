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
        self.geometry("1400x950")
        self.iconbitmap("logo.ico")
        # Inicializar conexiones
        self.mysql = MYSQL()
        self.sqlserver_manager = SQLSERVER()
        self.baremos = self.mysql.tabla_baremos()
        self.products_facturados = []
        self.products_enviados = []
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
        self.caso = tk.IntVar(value=1)  # 1 para Caso 1, 2 para Caso 2

        # Variables para la gestión de checkboxes
        self.checkbox_vars = []

        # Instanciar PDFGenerator
        self.pdf_generator = PDFGenerator(self, self.sqlserver_manager, bg="#0C4B85")
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
        header_frame.pack(fill=tk.X, pady=5)

        # Logo reducido
        logo_image = tk.PhotoImage(file="logos/logotrans.png").subsample(4, 4)
        tk.Label(header_frame, image=logo_image, bg="#0C4B85").pack(side=tk.LEFT, padx=5)

        # Número de control y botones de PDF en el mismo Frame
        control_pdf_frame = tk.Frame(header_frame, bg="#0C4B85")
        control_pdf_frame.pack(side=tk.LEFT, padx=10)

        # Número de Control
        tk.Label(control_pdf_frame, text="Nro de Control:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").grid(row=0, column=0, padx=5)
        tk.Entry(control_pdf_frame, textvariable=self.control_number, font=("Helvetica", 8), width=12).grid(row=0, column=1, padx=5)

        # Botones para generar PDFs
        self.simplified_pdf_button = tk.Button(control_pdf_frame, text="Generar PDF Almacen", command=lambda: self.generate_pdf_simplified(), bg="#0C4B85", fg="white", font=("Helvetica", 8))
        self.simplified_pdf_button.grid(row=0, column=2, padx=5)
        self.create_tooltip(self.simplified_pdf_button, "Genera el pdf que va al almacen")

        generate_pdf_button = tk.Button(control_pdf_frame, text="Generar PDF admin", command=lambda: self.generate_pdf(), bg="#0C4B85", fg="white", font=("Helvetica", 8))
        generate_pdf_button.grid(row=0, column=3, padx=5)
        self.create_tooltip(generate_pdf_button, "Genera el pdf  administrativo con costos, precios y rentabilidad")
        # Número de Pedido y Comedor en otro Frame
        control_frame = tk.Frame(header_frame, bg="#0C4B85")
        control_frame.pack(side=tk.LEFT, padx=10)

        # Número de Pedido
        tk.Label(control_frame, text="Nro de Pedido:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").grid(row=0, column=0, padx=5)
        tk.Entry(control_frame, textvariable=self.npedido, font=("Helvetica", 8), width=12).grid(row=0, column=1, padx=5)

        # Comedor
        tk.Label(control_frame, text="Comedor:", font=("Helvetica", 8, "bold"), bg="#0C4B85", fg="white").grid(row=0, column=2, padx=5)
        comedor_menu = ttk.Combobox(control_frame, textvariable=self.comedor, font=("Helvetica", 8), values=self.comedores['comedor'].sort_values().tolist(), width=50)
        comedor_menu.grid(row=0, column=3, padx=5)
        comedor_menu.bind("<<ComboboxSelected>>", self.update_product_options)

        # Botón para cambiar de caso
        self.change_case_button = tk.Button(header_frame, text="Cambiar caso", command=self.toggle_case, bg="#0C4B85", fg="white", font=("Helvetica", 8, "bold"))
        self.change_case_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.change_case_button, "Haga clic para alternar entre el caso 1 y el caso 2")

        # Sección de Productos
        self.product_frame = tk.Frame(scrollable_frame)
        self.product_frame.pack(fill=tk.X, pady=2)

        self.create_product_frames()

        # Instrucciones sobre cómo agregar productos y componentes en la misma línea
        control_row_frame = tk.Frame(scrollable_frame)
        control_row_frame.pack(fill=tk.X, pady=5)

        # Monto Faltante a la izquierda
        tk.Label(control_row_frame, text="Monto Faltante $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(side=tk.LEFT, padx=5)
        tk.Label(control_row_frame, textvariable=self.monto_faltante, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(side=tk.LEFT)
        tk.Label(control_row_frame, text="Una vez enviada la negociación ya no se puede editar", font=("Helvetica", 10), fg="black").pack(side=tk.LEFT, expand=True)
        delete_button = tk.Button(control_row_frame, text="Eliminar Producto Seleccionado", command=self.delete_selected_products, bg="#FF6347", fg="white", font=("Helvetica", 8, "bold"))
        delete_button.pack(side=tk.RIGHT, padx=5)

        # Crear tablas de productos facturados y enviados
        self.create_treeviews(scrollable_frame)

        # Botón de enviar negociación a la base de datos
        submit_button = tk.Button(scrollable_frame, text="Generar negociación", command=self.submit_negociacion, bg="#0C4B85", fg="white", font=("Helvetica", 9, "bold"))
        submit_button.pack(pady=5)
        self.create_tooltip(submit_button, "Guarde la negociación actual en la base de datos")

        # Necesario para que la imagen del logo se mantenga
        self.logo_image = logo_image

    def generate_pdf(self):
        # Obtener el número de control del Entry
        codclie = self.control_number.get().strip()
        if codclie:
            self.pdf_generator.generate_pdf(codclie)
        else:
            messagebox.showwarning("Advertencia", "Por favor, introduzca un Número de Control.")

    def generate_pdf_simplified(self):
        # Obtener el número de control del Entry
        codclie = self.control_number.get().strip()
        if codclie:
            self.pdf_generator.generate_pdf_simplified(codclie)
        else:
            messagebox.showwarning("Advertencia", "Por favor, introduzca un Número de Control.")
    
    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.wm_overrideredirect(True)
        tooltip_label = tk.Label(tooltip, text=text, background="yellow", relief='solid', borderwidth=1, font=("Helvetica", 8))
        tooltip_label.pack(ipadx=1)

        def show_tooltip(event):
            x = event.x_root + 20
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide_tooltip(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def update_treeview_headers(self):
        # Actualizar las columnas del Treeview para productos facturados
        self.tree_facturado["columns"] = ("Producto", "Cantidad a Facturar", "Precio Total $")
        self.tree_enviado["columns"] = ("Producto", "Cantidad a Enviar", "Precio Total $")

        # Configurar los encabezados para cada columna del Treeview
        for col in self.tree_facturado["columns"]:
            self.tree_facturado.heading(col, text=col)
            self.tree_facturado.column(col, anchor=tk.CENTER)  # Usar 'w' para alinear a la izquierda

        for col in self.tree_enviado["columns"]:
            self.tree_enviado.heading(col, text=col)
            self.tree_enviado.column(col, anchor=tk.CENTER)  # Usar 'w' para alinear a la izquierda

        # Ajustar el tamaño de las columnas específicas
        """self.tree_facturado.column("Producto", width=150)
        self.tree_enviado.column("Producto", width=150)
        self.tree_facturado.column("Cantidad a Facturar", width=130)
        self.tree_enviado.column("Cantidad a Enviar", width=130)
        self.tree_facturado.column("Precio Total $", width=85)
        self.tree_enviado.column("Precio Total $", width=85)"""

    def create_product_frames(self):
        for widget in self.product_frame.winfo_children():
            widget.destroy()

        left_frame = tk.Frame(self.product_frame)
        left_frame.pack(side=tk.LEFT, padx=7, pady=10, expand=True, fill=tk.BOTH)

        right_frame = tk.Frame(self.product_frame)
        right_frame.pack(side=tk.LEFT, padx=7, pady=10, expand=True, fill=tk.BOTH)

        if self.caso.get() == 1:
            self.create_product_frame(left_frame, "Producto Facturado", self.familiainicial, self.nominicial, self.codinicial,
                                      self.unidadinicial, self.solicitadoinicial, self.costodolarinicial, self.preciodolarinicial,
                                      self.preciototalinicial, filter_by_comedor=True)
            self.create_product_frame(right_frame, "Producto a Enviar", self.familianeg, self.nomneg, self.codneg,
                                      self.unidadneg, self.solicitadoneg, self.costodolarneg, self.preciodolarneg,
                                      self.preciototalneg, filter_by_comedor=False, is_negotiated=True)
        else:
            self.create_product_frame(left_frame, "Producto a Enviar", self.familianeg, self.nomneg, self.codneg,
                                      self.unidadneg, self.solicitadoneg, self.costodolarneg, self.preciodolarneg,
                                      self.preciototalneg, filter_by_comedor=False, is_negotiated=True)
            self.create_product_frame(right_frame, "Producto Facturado", self.familiainicial, self.nominicial, self.codinicial,
                                      self.unidadinicial, self.solicitadoinicial, self.costodolarinicial, self.preciodolarinicial,
                                      self.preciototalinicial, filter_by_comedor=True)

    def create_treeviews(self, parent):
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.X, pady=5)

        # Crear el Treeview de productos facturados
        self.tree_facturado = ttk.Treeview(tree_frame, columns=("Producto", "Cantidad a Facturar", "Precio Total $"), show="headings", height=5)
        self.tree_facturado.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Configurar los encabezados y columnas de productos facturados
        self.tree_facturado.heading("Producto", text="Producto")
        self.tree_facturado.heading("Cantidad a Facturar", text="Cantidad a Facturar")
        self.tree_facturado.heading("Precio Total $", text="Precio Total $")
        self.tree_facturado.column("Producto", anchor=tk.CENTER, width=140)
        self.tree_facturado.column("Cantidad a Facturar", anchor=tk.CENTER, width=100)
        self.tree_facturado.column("Precio Total $", anchor=tk.CENTER, width=85)

        # Crear el Treeview de productos enviados
        self.tree_enviado = ttk.Treeview(tree_frame, columns=("Producto", "Cantidad a Enviar", "Precio Total $"), show="headings", height=5)
        self.tree_enviado.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Configurar los encabezados y columnas de productos enviados
        self.tree_enviado.heading("Producto", text="Producto")
        self.tree_enviado.heading("Cantidad a Enviar", text="Cantidad a Enviar")
        self.tree_enviado.heading("Precio Total $", text="Precio Total $")
        self.tree_enviado.column("Producto", anchor=tk.CENTER, width=140)
        self.tree_enviado.column("Cantidad a Enviar", anchor=tk.W, width=130)
        self.tree_enviado.column("Precio Total $", anchor=tk.W, width=85)

    def update_monto_faltante(self):
        # Calcular el monto faltante basado en el caso seleccionado
        if self.caso.get() == 1:
            # Caso 1: La lógica permanece igual
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            self.monto_faltante.set(round(self.preciototalinicial.get() - total_enviado, 2))

            if self.monto_faltante.get() > 0 and self.preciodolarneg.get() > 0:
                self.cantidad_sugerida.set(int(self.monto_faltante.get() / self.preciodolarneg.get()))
            else:
                self.cantidad_sugerida.set(0)
        else:
            # Caso 2: Actualizar el monto faltante basado en productos a enviar
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            self.monto_faltante.set(round(total_enviado, 2))

            # Calcular la cantidad sugerida para los productos facturados
            if self.monto_faltante.get() > 0 and self.preciodolarinicial.get() > 0:
                self.cantidad_sugerida.set(int(self.monto_faltante.get() / self.preciodolarinicial.get()))
            else:
                self.cantidad_sugerida.set(0)

    def create_product_frame(self, parent, title, familia_var, nombre_var, codigo_var, unidad_var, cantidad_var, costo_var, precio_var, precio_total_var, filter_by_comedor=False, is_negotiated=False):
        frame = tk.LabelFrame(parent, text=title, font=("Helvetica", 8, "bold"), padx=5, pady=5, bg="#F0F0F0")
        frame.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

        if self.caso.get() == 1:
            if title == "Producto Facturado":
                instruction_text = "Coloque la cantidad y costo, luego puede agregar el producto. No deje espacios vacíos"
            else:
                instruction_text = "Precio automático anclado al costo, debe colocarlo para que le indique la cantidad sugerida."
        else:
            if title == "Producto a Enviar":
                instruction_text = "Coloque la cantidad y el costo antes de agregar el producto."
            else:
                instruction_text = "Cantidad sugerida se actualiza al seleccionar el producto, el costo no debe quedar vacío."

        tk.Label(frame, text=instruction_text, font=("Helvetica", 8, "bold"), fg="red", bg="#F0F0F0").pack(pady=2, anchor="w")

        tk.Label(frame, text="Familia:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        tk.Label(frame, textvariable=familia_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        tk.Label(frame, text="Descripción del Producto:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        product_menu = ttk.Combobox(frame, textvariable=nombre_var, font=("Helvetica", 8), width=20)
        product_menu.pack(fill=tk.X, padx=2)
        product_menu.bind("<<ComboboxSelected>>", lambda _: self.update_product_info(nombre_var, codigo_var, familia_var, unidad_var, precio_var))

        if filter_by_comedor:
            # Para productos facturados que dependen del comedor
            self.product_menu_inicial = product_menu
            # Actualizar dinámicamente las opciones según el comedor seleccionado
            product_menu['values'] = self.baremos[self.baremos['comedor'] == self.comedor.get()]['descripcion_zudalpro'].sort_values().unique().tolist()
            # Filtrado dinámico para el producto facturado
            
        else:
        # Para productos enviados que son libres
            all_products = self.baremos['descripcion_zudalpro'].sort_values().unique().tolist()
            product_menu['values'] = all_products
            # Filtrado dinámico para el producto enviado
            product_menu.bind("<KeyRelease>", lambda event: self.filter_combobox(event, product_menu, all_products))

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
        tk.Label(frame, textvariable=precio_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        tk.Label(frame, text="Precio Total $:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
        tk.Label(frame, textvariable=precio_total_var, font=("Helvetica", 8), bg="#F0F0F0").pack(pady=2, anchor="w")

        if is_negotiated and self.caso.get() == 1:
            tk.Label(frame, text="Cantidad Sugerida:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
            tk.Label(frame, textvariable=self.cantidad_sugerida, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(pady=2, anchor="w")
        elif not is_negotiated and self.caso.get() == 2:
            tk.Label(frame, text="Cantidad Sugerida:", font=("Helvetica", 8, "bold"), bg="#F0F0F0").pack(pady=2, anchor="w")
            tk.Label(frame, textvariable=self.cantidad_sugerida, font=("Helvetica", 10, "bold"), bg="#F0F0F0", fg="#0C4B85").pack(pady=2, anchor="w")

        if title == "Producto Facturado":
           tk.Button(frame, text="Agregar Producto Facturado", command=self.add_product_facturado, bg="#008f39", fg="white", font=("Helvetica", 8)).pack(pady=2)
           
        else:
            tk.Button(frame, text="Agregar Producto Enviado", command=self.add_product_enviado, bg="#008f39", fg="white", font=("Helvetica", 8)).pack(pady=2)
            
    def filter_combobox(self, event, combobox, original_values):
        """
        Filtra dinámicamente las opciones en el combobox basado en la entrada del usuario.
        """
        # Obtener el texto ingresado por el usuario
        typed_text = combobox.get()

        # Filtrar las opciones basadas en el texto ingresado solo si el texto coincide con el comienzo de las opciones
        if typed_text == '':
            combobox['values'] = original_values  # Mostrar todas las opciones si no hay texto
        else:
            filtered_values = [item for item in original_values if item.lower().startswith(typed_text.lower())]
            combobox['values'] = filtered_values  # Mostrar solo las opciones que comienzan con el texto ingresado

        combobox.event_generate('<Down>') # Desplegar la lista filtrada
    
    def update_product_options(self, _):
        comedor = self.comedor.get()
        filtered_unidades = self.baremos[self.baremos['comedor'] == comedor]['descripcion_zudalpro'].sort_values().unique().tolist()
        self.product_menu_inicial['values'] = filtered_unidades

    def update_product_info(self, nombre_var, codigo_var, familia_var, unidad_var, precio_var):
        nombre_producto = nombre_var.get()
        filtered_data = self.baremos[self.baremos['descripcion_zudalpro'] == nombre_producto]
        if not filtered_data.empty:
            codigo_var.set(filtered_data['codzudalpro'].values[0].strip())
            familia_var.set(filtered_data['familia'].values[0].strip())
            presentaciones = filtered_data['presentacion'].sort_values().unique().tolist()
            self.unidad_menu['values'] = presentaciones
            unidad_var.set(presentaciones[0].strip() if presentaciones else '')

            if self.caso.get() == 1:
                if nombre_var == self.nomneg:
                    # Caso 1: Producto Enviado - Precio se calcula con el costo/0.65
                    costo_unitario = self.costodolarneg.get()
                    if costo_unitario:
                        self.preciodolarneg.set(round(costo_unitario / 0.65, 2))
                    self.calculate_suggested_quantity_case_1()

                elif nombre_var == self.nominicial:
                    # Caso 1: Producto Facturado
                    precio_var.set(filtered_data['precio'].values[0])
                    self.calculate_suggested_quantity_case_1()
            
            elif self.caso.get() == 2:
                if nombre_var == self.nominicial:
                    # Caso 2: Producto Facturado
                    precio_var.set(filtered_data['precio'].values[0])
                    self.calculate_suggested_quantity_case_2()

                elif nombre_var == self.nomneg:
                    # Caso 2: Producto Enviado - Precio se calcula con el costo/0.65
                    costo_unitario = self.costodolarneg.get()
                    if costo_unitario:
                        self.preciodolarneg.set(round(costo_unitario / 0.65, 2))
                    self.calculate_suggested_quantity_case_2()

    def calculate_suggested_quantity_case_1(self):
        # Calcula la cantidad sugerida para el Caso 1
        if self.preciodolarneg.get() > 0:
            total_facturado = sum(product['precio_total_inicial'] for product in self.products_facturados)
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            monto_faltante = total_facturado - total_enviado
            cantidad_sugerida = max(monto_faltante / self.preciodolarneg.get(), 0)
            self.cantidad_sugerida.set(int(cantidad_sugerida))
        else:
            self.cantidad_sugerida.set(0)

    def calculate_suggested_quantity_case_2(self):
        # Calcula la cantidad sugerida para el Caso 2
        if self.preciodolarinicial.get() > 0:
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            total_facturado = sum(product['precio_total_inicial'] for product in self.products_facturados)
            monto_faltante = total_enviado - total_facturado
            cantidad_sugerida = max(monto_faltante / self.preciodolarinicial.get(), 0)
            self.cantidad_sugerida.set(int(cantidad_sugerida))
        else:
            self.cantidad_sugerida.set(0)

    def add_product_facturado(self):
        try:
            if not self.control_number.get():
                messagebox.showwarning("Advertencia", "El Numero de control no puede quedar vacío.")
                return
            if self.costodolarinicial.get() == 0 or self.costodolarinicial.get() == '':
                messagebox.showwarning("Advertencia", "El costo del Producto no puede quedar vacío o ser 0.")
                return
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
                'precio_total_inicial': round(self.preciodolarinicial.get() * self.solicitadoinicial.get(), 2)
            }
            self.products_facturados.append(data)
            self.update_table_facturado()
            if self.caso.get() == 2:
                total_facturado = sum(product['precio_total_inicial'] for product in self.products_facturados)
                monto_faltante_actual = self.total_enviado.get() - total_facturado
                self.monto_faltante.set(round(monto_faltante_actual, 2))
            else:
                self.update_monto_faltante()   # Actualizar el monto faltante después de agregar el producto
        except:
            messagebox.showerror("Advertencia", "El costo del Producto no puede quedar vacío.")

    def add_product_enviado(self):
        try:
            if not self.control_number.get():
                messagebox.showwarning("Advertencia", "El Numero de control no puede quedar vacío.")
                return
            if self.costodolarneg.get() == 0 or self.costodolarneg.get() == '':
                messagebox.showwarning("Advertencia", "El costo del Producto no puede quedar vacío o ser 0.")
                return
            data = {
                'codclie': self.control_number.get().strip(),
                'fechaneg': datetime.today().strftime('%Y-%m-%d'),
                'comedor': self.comedor.get().strip(),
                'npedido': self.npedido.get().strip(),
                'familianeg': self.familianeg.get().strip(),
                'codneg': self.codneg.get().strip(),
                'nomneg': self.nomneg.get().strip(),
                'undneg': self.unidadneg.get().strip(),
                'solicitadoneg': self.solicitadoneg.get(),
                'costodolarneg': self.costodolarneg.get(),
                'preciodolarneg': self.preciodolarneg.get(),
                'precio_total_neg': round(self.preciodolarneg.get() * self.solicitadoneg.get(), 2)
            }
            self.products_enviados.append(data)
            self.update_table_enviado()

        # Actualizar el monto faltante basado en la suma de productos enviados en Caso 2
            if self.caso.get() == 2:
                total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
                self.total_enviado.set(total_enviado)
                self.monto_faltante.set(round(total_enviado, 2))  # Inicializa el monto faltante como total de enviados
            else:
                self.update_monto_faltante()  # Actualizar el monto faltante después de agregar el producto
        except:
             messagebox.showerror("Advertencia", "El costo del Producto no puede quedar vacío.")

    def update_monto_faltante(self):
        # Calcular el total del precio de los productos enviados
        if self.caso.get() == 2:
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            total_facturado = sum(product['precio_total_inicial'] for product in self.products_facturados)
            
            # Calcular el monto faltante basado en la diferencia
            self.monto_faltante.set(round(total_enviado - total_facturado, 2))
        else:
            total_enviado = sum(product['precio_total_neg'] for product in self.products_enviados)
            self.monto_faltante.set(round(sum(product['precio_total_inicial'] for product in self.products_facturados) - total_enviado, 2))
        
        # Calcular la cantidad sugerida en función del monto faltante total
        if self.monto_faltante.get() > 0 and self.preciodolarneg.get() > 0:
            self.cantidad_sugerida.set(int(self.monto_faltante.get() / self.preciodolarneg.get()))
        else:
            self.cantidad_sugerida.set(0)

    def update_table_facturado(self):
        for i in self.tree_facturado.get_children():
            self.tree_facturado.delete(i)
        for product in self.products_facturados:
            self.tree_facturado.insert("", tk.END, values=(
               product['nominicial'], product['solicitadoinicial'], product['precio_total_inicial']
            ))

    def update_table_enviado(self):
        for i in self.tree_enviado.get_children():
            self.tree_enviado.delete(i)
        for product in self.products_enviados:
            self.tree_enviado.insert("", tk.END, values=(
                product['nomneg'], product['solicitadoneg'], product['precio_total_neg']
            ))

    def toggle_case(self):
        self.caso.set(2 if self.caso.get() == 1 else 1)
        self.create_product_frames()
        self.clear_values()
        self.update_treeview_headers()

    def clear_values(self):
    # Limpiar todas las variables de control excepto el número de control
        self.comedor.set("")
        self.npedido.set("")
        self.familiainicial.set("")
        self.codinicial.set("")
        self.nominicial.set("")
        self.unidadinicial.set("")
        self.solicitadoinicial.set(0)
        self.costodolarinicial.set(0.0)
        self.preciodolarinicial.set(0.0)
        self.preciototalinicial.set(0.0)

        self.familianeg.set("")
        self.codneg.set("")
        self.nomneg.set("")
        self.unidadneg.set("")
        self.solicitadoneg.set(0)
        self.costodolarneg.set(0.0)
        self.preciodolarneg.set(0.0)
        self.preciototalneg.set(0.0)
        self.cantidad_sugerida.set(0)

        self.monto_faltante.set(0.0)
        self.monto_faltante_actual.set(0.0)
        self.facturado_procesado = False
        self.total_enviado.set(0.0)

        # Limpiar las listas de productos
        self.products_facturados.clear()
        self.products_enviados.clear()

        # Limpiar los Treeviews
        self.update_table_facturado()
        self.update_table_enviado()

    def calculate_price_total(self, cantidad_var, precio_var, precio_total_var, is_negotiated):
        try:
            cantidad = cantidad_var.get()

            # Calcular el precio unitario en el caso de producto a enviar y costo ingresado
            if is_negotiated:
                costo_unitario = self.costodolarneg.get()
                if costo_unitario:
                    # Calcular el precio usando la fórmula costo/0.65
                    self.preciodolarneg.set(round(costo_unitario / 0.65, 2))
                precio_unitario = self.preciodolarneg.get()

            else:
                precio_unitario = precio_var.get()  # Precio traído desde la tabla baremos

            if cantidad == '':
                cantidad = 0
            if precio_unitario == '':
                precio_unitario = 0

            # Calcular el precio total
            total = round(float(cantidad) * float(precio_unitario), 2)
            precio_total_var.set(round(total, 2))

            # Actualizar la cantidad sugerida después de calcular el precio total
            if self.caso.get() == 1:
                self.calculate_suggested_quantity_case_1()
            else:
                self.calculate_suggested_quantity_case_2()

        except Exception as e:
            print(f"Error al calcular el precio total: {e}")

    def delete_selected_products(self):
        # Obtener el producto seleccionado en el Treeview de productos facturados
        selected_facturado = self.tree_facturado.selection()
        if selected_facturado:
            for item in selected_facturado:
                item_index = self.tree_facturado.index(item)
                del self.products_facturados[item_index]
                self.tree_facturado.delete(item)

        # Obtener el producto seleccionado en el Treeview de productos enviados
        selected_enviado = self.tree_enviado.selection()
        if selected_enviado:
            for item in selected_enviado:
                item_index = self.tree_enviado.index(item)
                del self.products_enviados[item_index]
                self.tree_enviado.delete(item)

        # Actualizar el monto faltante después de eliminar productos
        self.update_monto_faltante()
    
    def submit_negociacion(self):
        try:
            for product in self.products_facturados + self.products_enviados:
                product['codclie'] = product['codclie'].strip()
                product['comedor'] = product['comedor'].strip()
                product['npedido'] = product['npedido'].strip()

            df_facturados = pd.DataFrame(self.products_facturados)
            df_enviados = pd.DataFrame(self.products_enviados)

            # Realizar los cálculos
            df_facturados['costototaldolarinicial'] = df_facturados['solicitadoinicial'] * df_facturados['costodolarinicial']
            df_facturados['preciototaldolarinicial'] = df_facturados['solicitadoinicial'] * df_facturados['preciodolarinicial']
            df_facturados['rentabilidadinicial'] = ((df_facturados['preciodolarinicial'] - df_facturados['costodolarinicial']) / df_facturados['preciodolarinicial']) * 100
            df_facturados['utilidadinicial'] = df_facturados['preciototaldolarinicial'] - df_facturados['costototaldolarinicial']
            
            df_enviados['preciototaldolarneg'] = df_enviados['solicitadoneg'] * df_enviados['preciodolarneg']
            df_enviados['costototaldolarneg'] = df_enviados['solicitadoneg'] * df_enviados['costodolarneg']
            df_enviados['rentabilidadneg'] = ((df_enviados['preciodolarneg'] - df_enviados['costodolarneg']) / df_enviados['preciodolarneg']) * 100
            df_enviados['utilidadneg'] = df_enviados['preciototaldolarneg'] - df_enviados['costototaldolarneg']

            # Eliminar columnas innecesarias
            columns_to_remove = ['precio_total_neg', 'precio_total_inicial']
            df_facturados = df_facturados.drop(columns=[col for col in columns_to_remove if col in df_facturados.columns])
            df_enviados = df_enviados.drop(columns=[col for col in columns_to_remove if col in df_enviados.columns])

            # Intentar insertar datos en la tabla "Facturados"
            result_message_facturados = self.sqlserver_manager.add_data('TablaFacturados', df_facturados)
            
            # Intentar insertar datos en la tabla "Enviados"
            result_message_enviados = self.sqlserver_manager.add_data('TablaEnviados', df_enviados)

            # Verificar mensajes de resultado
            if "exitosamente" in result_message_facturados and "exitosamente" in result_message_enviados:
                messagebox.showinfo("Información enviada", "Negociacion creada con éxito.")
                self.clear_values()  # Limpiar todas las variables excepto el número de control
            else:
                messagebox.showerror("Error", f"Error al crear la negociación verifica tener acceso al 'WIFI ZudalproCorp':\n\n tabla facturados {result_message_facturados}\n\n tabla Enviados: {result_message_enviados}")

        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error inesperado: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()