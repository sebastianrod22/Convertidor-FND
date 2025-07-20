import tkinter as tk
from tkinter import ttk, font
import formaNormal

class programa:

    def __init__(self, master, r_callback= None):
        self.master = master
        self.master.title("Convertidor a FND")
        self.master.config(background="#DCDAD5")
        self.master.resizable(False, False)
        self.r_callback = r_callback

        self.entrada = tk.StringVar()

        self.ventana(1200, 550)
        self.widgets()

    #Centra la ventana
    def ventana(self, ancho, alto):
        pantalla_ancho = self.master.winfo_screenwidth()
        pantalla_alto = self.master.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.master.geometry(f"{ancho}x{alto}+{x}+{y}")

    #Crea los widgets y el treeview
    def widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        ttk.Label(self.master, 
                  text="Ingrese su formula bien formada:", 
                  font=('Palatino Linotype', 20),
                  background="#dcdad5",
                  foreground="#474747",
                  ).pack(pady=(10, 10))
        
        frame = ttk.Frame(self.master)
        frame.pack(fill='both', expand=True, padx=50)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(0, weight=3)

        tk.Label(self.master, 
                 text="Formula Normal Disyuntiva:",
                 font=('Palatino Linotype', 20),
                 background="#dcdad5",
                 foreground="#474747",
                 ).pack(pady=(10, 10))
        
        ttk.Label(frame, 
                  text='  Formula:'
                  ).grid(column=0, row=0, sticky=tk.W)
        
        self.entry = ttk.Entry(frame, 
                               width=120)
        
        self.entry.grid(column=1, 
                        row=0, 
                        sticky=tk.W, 
                        pady=(10, 10),
                        padx=(10,10))

        ttk.Button(frame, 
                   text='Calcular FND',
                   command= self.dnf
                   ).grid(column=1, row=1, sticky=tk.N)

        self.treeview = ttk.Treeview(columns=("0", "1"))
        style = ttk.Style()
        style.configure("Treeview", font=('Palatino Linotype', 10))
        self.treeview.heading("0",
                              text="Regla")
        self.treeview.column("0", 
                             width=10, 
                             minwidth=10)
        self.treeview.heading("1",
                              text="Expresión")
        self.treeview.column("1", 
                             width=700, 
                             minwidth=0)
        self.treeview['show'] = 'headings'


        self.treeview.pack(fill=tk.BOTH, 
                            expand=True, 
                            padx=10, 
                            pady=10,)
        
        
        ttk.Button(
                   text='Copiar formula seleccionada',
                   command= self.copiar_formula,
                   ).pack(padx=10, pady=10)
        
    #Habilita el boton de copiar formula    
    def copiar_formula(self):
        id = self.treeview.selection()
        if len(self.treeview.get_children()) == 0:
            return
        else:
            if len(self.treeview.selection()) == 0:
                return
            return root.clipboard_append(self.treeview.item(id[0],"values")[1])
    
    #Obtiene la formula DNF de formaNormal.py
    def dnf(self):
        self.treeview.delete(*self.treeview.get_children())
        entrada = str(self.entry.get()).replace('\\', '\\\\')
        if entrada =="":
            self.treeview.insert("", 
                                 tk.END,
                                 values=("No hay formula",""))  
        else:
            try:
                arbol = formaNormal.forma_normal(entrada)
            except:
                self.treeview.insert("", 
                                 tk.END,
                                 values=("No hay formula bien formada ","")) 
                return

            for i in range(len(arbol)):
                self.treeview.insert("", 
                                     tk.END,
                                     values= (arbol[i][0], arbol[i][1]))
if __name__ == "__main__":
    root = tk.Tk()
    programa(root)
    root.mainloop()

#Casos de prueba
#(\neg( (\neg p \lor \neg  q) \rightarrow \neg (p \land q)))
#\neg (p \land (q \rightarrow r))
#\neg(\neg p \lor \neg q)
#(A \leftrightarrow B) \land C