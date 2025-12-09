
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk, ImageEnhance

# Intentar cargar pygame para sonidos (opcional)
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

# ---------------------------
# Datos del juego (igual que tu código)
# ---------------------------

REGLAS_INMUTABLES = (
    "REGLAS:",
    " - Se aceptan respuestas sin importar mayúsculas/minúsculas.",
    " - Escribe 'INVENTARIO' para ver tus pistas.",
    " - Escribe 'TERMINAR' para salir del juego.",
    " - ¡Cuidado con los espacios extra! Debes ingresar solo la respuesta.",
)

MENSAJES_ERROR = (
    " ¡CRACK! La cerradura no cede. Inténtalo de nuevo.",
    " Respuesta incorrecta. No hay atajos aquí.",
    " La respuesta no coincide con la llave esperada.",
)

MAPA_ESCAPE = {
    'Biblioteca Antigua': {
        'descripcion': "Estás en una polvorienta biblioteca. Para abrir la siguiente puerta, debes saber: ¿Cuál es el planeta más cercano al Sol?",
        'respuesta_correcta': 'mercurio',
        'recompensa': 'llave_bronce',
        'siguiente_sala': 'Sala de Arte',
        'prerequisito': "",
    },
    'Sala de Arte': {
        'descripcion': "Estás frente a un caballete vacío. Una placa dice: 'Solo el autor de la Gioconda puede desbloquear la paleta'. ¿Quién pintó la famosa obra “La Mona Lisa” (solo el apellido del nombre más conocido)?",
        'respuesta_correcta': 'davinci',
        'recompensa': 'mapa_antiguo',
        'siguiente_sala': 'Laboratorio Oculto',
        'prerequisito': 'llave_bronce',
    },

    'Laboratorio Oculto': {
        'descripcion': "La puerta está cifrada. Solo el nombre del 'viejo continente' puede cederla. Necesitas el mapa_antiguo para ver el teclado de la cerradura.",
        'respuesta_correcta': 'europa',
        'recompensa': 'formula_gravedad',
        'siguiente_sala': 'Jardin de Manzanas',
        'prerequisito': 'mapa_antiguo',
    },
    
    'Jardin de Manzanas': {
        'descripcion': "Estás en un jardín bajo un árbol. ¿Qué famoso científico descubrió la ley de la gravedad al observar una manzana caer? (Solo el apellido)",
        'respuesta_correcta': 'newton',
        'recompensa': 'codigo_final',
        'siguiente_sala': 'Observatorio Final',
        'prerequisito': 'formula_gravedad',
    },

    'Observatorio Final': {
        'descripcion': "Frente a ti hay un pedestal con una antorcha. Para abrir el candado de la salida, debes introducir el país donde se originaron los Juegos Olímpicos.",
        'respuesta_correcta': 'grecia',
        'recompensa': 'pase_de_escape',
        'siguiente_sala': 'Salida', 
        'prerequisito': 'codigo_final',
    }
}

# ---------------------------
# Rutas por defecto (ajusta si quieres)
# ---------------------------

IMAGENES_SALAS = {
    'Biblioteca Antigua': 'biblioteca.png',
    'Sala de Arte': 'arte.png',
    'Laboratorio Oculto': 'laboratorio.png',
    'Jardin de Manzanas': 'jardin.png',
    'Observatorio Final': 'observatorio.png',
}

ICONOS_INVENTARIO = {
    'llave_bronce': 'icon_llave.png',
    'mapa_antiguo': 'icon_mapa.png',
    'formula_gravedad': 'icon_formula.png',
    'codigo_final': 'icon_codigo.png',
    'pase_de_escape': 'icon_pase.png',
}

SONIDOS = {
    'correcto': 'sonido_correcto.wav',
    'error': 'sonido_error.wav',
    'paso': 'sonido_paso.wav',
}

# ---------------------------
# Funciones de conversión (manteniendo tu lógica)
# ---------------------------

def a_minusculas(texto):
    """
    Función para convertir texto a minúsculas sin usar .lower(), ord() o chr().
    Uso de mapeo manual (como en tu código).
    """
    mapa_mayusculas = {
        'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f', 'G': 'g', 
        'H': 'h', 'I': 'i', 'J': 'j', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 
        'O': 'o', 'P': 'p', 'Q': 'q', 'R': 'r', 'S': 's', 'T': 't', 'U': 'u', 
        'V': 'v', 'W': 'w', 'X': 'x', 'Y': 'y', 'Z': 'z'
    }
    resultado = ""
    for caracter in texto:
        if caracter in mapa_mayusculas:
            resultado = resultado + mapa_mayusculas[caracter]
        else:
            resultado = resultado + caracter
    return resultado

def a_mayusculas(texto):
    """
    Función para convertir texto a mayúsculas sin usar .upper(), ord() o chr().
    """
    mapa_minusculas = {
        'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G', 
        'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 
        'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U', 
        'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z'
    }
    resultado = ""
    for caracter in texto:
        if caracter in mapa_minusculas:
            resultado = resultado + mapa_minusculas[caracter]
        else:
            resultado = resultado + caracter
    return resultado

# ---------------------------
# Funciones originales adaptadas a GUI
# ---------------------------

def mostrar_bienvenida_console():
    """Función auxiliar (usada si ejecutas desde consola)."""
    print("          ESCAPE ROOM DE CONOCIMIENTO        ")
    print("Tu conocimiento es la única llave. Resuelve los acertijos\n")
    for linea in REGLAS_INMUTABLES:
        print(linea)

def mostrar_inventario_console(inventario):
    """
    Igual que tu función: imprime inventario en consola.
    """
    if inventario:
        print("TU INVENTARIO")
        salida = ""
        for item in inventario:
            salida = salida + item + ", "
        print("Objetos y Códigos: " + salida[0:-2])
        print("====================\n")
    else:
        print("[Bolsillo vacío] No has ganado ninguna pista aún.")

def tiene_prerequisito(sala_actual, inventario):
    """
    Verifica si el jugador tiene el objeto requerido en el inventario.
    (idéntica a tu versión)
    """
    if 'prerequisito' in MAPA_ESCAPE[sala_actual]:
        prereq = MAPA_ESCAPE[sala_actual]['prerequisito']
    else:
        prereq = ""

    if prereq == "":
        return True, "" 

    for item in inventario:
        if item == prereq:
            return True, " ¡Tienes el objeto: " + prereq + "! La pista es visible ahora."

    return False, " Necesitas el objeto/código: " + prereq + " para interactuar con este desafío."

def validar_respuesta(entrada_usuario, sala_actual, inventario):
    """
    Mantiene la firma y lógica de tu función: devuelve True, False o 'TERMINAR'.
    (En la GUI la usaremos pero mostraremos mensajes con ventanas.)
    """
    data_sala = MAPA_ESCAPE[sala_actual]
    respuesta_esperada = data_sala['respuesta_correcta']
    
    entrada_min = a_minusculas(entrada_usuario)
    
    if entrada_min == respuesta_esperada:
        
        tiene, mensaje = tiene_prerequisito(sala_actual, inventario)
        
        if tiene:
            # equivalente a imprimir "¡CLIC! Respuesta correcta..."
            return True
        else:
            # no tiene prereq
            return False

    elif entrada_min == 'terminar':
        return 'TERMINAR' 

    else:
        return False

# ---------------------------
# GUI: clase principal
# ---------------------------

class EscapeRoomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Escape Room de Conocimiento - Interactivo")
        self.root.configure(bg="#7a7adf")
        self.fullscreen = True
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Estado del juego
        self.inventario = []
        self.ubicacion_actual = 'Biblioteca Antigua'

        # caché de imágenes / iconos
        self.imagenes_cache = {}
        self.iconos_cache = {}

        # UI
        self._crear_layout()

        # cargar recursos en background
        self._cargar_recursos()

        # mostrar sala inicial (con animación)
        self._cargar_sala(initial=True)

    # ----- UI -----
    def _crear_layout(self):
        # HUD superior
        hud = tk.Frame(self.root, bg="#081024", height=64)
        hud.pack(fill='x', side='top')

        self.lbl_titulo = tk.Label(hud, text="ESCAPE ROOM DE CONOCIMIENTO", bg="#081024", fg="white",
                                   font=("Segoe UI", 18, "bold"))
        self.lbl_titulo.pack(side='left', padx=20)

        btn_reglas = tk.Button(hud, text="Reglas", command=self._ventana_reglas, bg="#13203b", fg="white", bd=0, padx=10, pady=6)
        btn_reglas.pack(side='right', padx=12)
        self._hover(btn_reglas)

        btn_inv = tk.Button(hud, text="Inventario", command=self._ventana_inventario, bg="#13203b", fg="white", bd=0, padx=10, pady=6)
        btn_inv.pack(side='right', padx=6)
        self._hover(btn_inv)

        # Main
        main = tk.Frame(self.root, bg="#68a5bc")
        main.pack(fill='both', expand=True, padx=16, pady=12)

        # Left: imagen + descripción
        left = tk.Frame(main, bg="#29006a")
        left.pack(side='left', fill='both', expand=True)

        self.canvas = tk.Canvas(left, width=800, height=480, bg="#5d6392", highlightthickness=0)
        self.canvas.pack(padx=12, pady=12)

        self.lbl_descripcion = tk.Label(left, text="", bg="#0b0b12", fg="#000000", font=("Segoe UI", 13), wraplength=760, justify='left')
        self.lbl_descripcion.pack(padx=12)

        # Right: chat narrativo + inventario iconos
        right = tk.Frame(main, bg="#071024", width=320)
        right.pack(side='right', fill='y')

        lbl_chat = tk.Label(right, text="Narrativa", bg="#071024", fg="white", font=("Segoe UI", 12, "bold"))
        lbl_chat.pack(pady=(12,4))

        self.chat = ScrolledText(right, width=36, height=18, bg="#051025", fg="#cfe7ff", font=("Consolas", 10))
        self.chat.pack(padx=8, pady=6)
        self.chat.config(state='disabled')

        lbl_inv = tk.Label(right, text="Inventario", bg="#071024", fg="white", font=("Segoe UI", 12, "bold"))
        lbl_inv.pack(pady=(6,4))

        self.frame_icons = tk.Frame(right, bg="#071024")
        self.frame_icons.pack(padx=8, pady=6)

        # Bottom: entrada y botones
        bottom = tk.Frame(self.root, bg="#020317", height=80)
        bottom.pack(fill='x', side='bottom')

        self.entry = tk.Entry(bottom, font=("Segoe UI", 14), width=80)
        self.entry.pack(side='left', padx=20, pady=16)
        self.entry.bind("<Return>", lambda e: self._on_enviar())

        self.btn_enviar = tk.Button(bottom, text="Enviar", command=self._on_enviar, bg="#3b82f6", fg="white", font=("Segoe UI", 11), bd=0, padx=12, pady=6)
        self.btn_enviar.pack(side='left', padx=8)
        self._hover(self.btn_enviar)

        self.btn_pista = tk.Button(bottom, text="Pista", command=self._on_pista, bg="#10b981", fg="white", font=("Segoe UI", 11), bd=0, padx=12, pady=6)
        self.btn_pista.pack(side='left', padx=8)
        self._hover(self.btn_pista)

    def _hover(self, widget):
        orig = widget['bg']
        def enter(e):
            widget['bg'] = "#5b67ff"
        def leave(e):
            widget['bg'] = orig
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # ----- recursos -----
    def _cargar_recursos(self):
        # cargar imágenes de sala si existen
        for sala, ruta in IMAGENES_SALAS.items():
            if os.path.exists(ruta):
                try:
                    img = Image.open(ruta).convert('RGBA')
                    # escalamos a canvas target (800x480)
                    img = img.resize((800,480), Image.LANCZOS)
                    self.imagenes_cache[sala] = img
                except Exception:
                    self.imagenes_cache[sala] = None
            else:
                self.imagenes_cache[sala] = None

        # cargar iconos inventario (64x64)
        for key, ruta in ICONOS_INVENTARIO.items():
            if os.path.exists(ruta):
                try:
                    img = Image.open(ruta).convert('RGBA')
                    img = img.resize((64,64), Image.LANCZOS)
                    self.iconos_cache[key] = ImageTk.PhotoImage(img)
                except Exception:
                    self.iconos_cache[key] = None
            else:
                self.iconos_cache[key] = None

    def _reproducir_sonido(self, clave):
        if not PYGAME_AVAILABLE:
            return
        ruta = SONIDOS.get(clave)
        if ruta and os.path.exists(ruta):
            try:
                s = pygame.mixer.Sound(ruta)
                s.play()
            except Exception:
                pass

    # ----- ventanas utility -----
    def _ventana_reglas(self):
        win = tk.Toplevel(self.root)
        win.title("Reglas")
        win.configure(bg="#081024")
        txt = "\n".join(REGLAS_INMUTABLES)
        lbl = tk.Label(win, text=txt, font=("Segoe UI", 12), bg="#081024", fg="white", justify='left')
        lbl.pack(padx=12, pady=12)

    def _ventana_inventario(self):
        win = tk.Toplevel(self.root)
        win.title("Inventario")
        win.configure(bg="#081024")
        cont = tk.Frame(win, bg="#081024")
        cont.pack(padx=12, pady=12)
        if not self.inventario:
            tk.Label(cont, text="Inventario vacío", bg="#081024", fg="white").pack()
            return
        for it in self.inventario:
            frame = tk.Frame(cont, bg="#081024", padx=6, pady=6)
            frame.pack(side='left')
            icon = self.iconos_cache.get(it)
            if icon:
                lbl = tk.Label(frame, image=icon, bg="#081024")
                lbl.image = icon
                lbl.pack()
            else:
                tk.Label(frame, text=it, bg="#1e2430", fg="white", width=10, height=4).pack()
            tk.Label(frame, text=it, bg="#081024", fg="white", font=("Segoe UI", 9)).pack()

    # ----- chat narrativo -----
    def _append_chat(self, texto):
        self.chat.config(state='normal')
        self.chat.insert('end', texto + "\n")
        self.chat.see('end')
        self.chat.config(state='disabled')

    # ----- cargar sala (con animación) -----
    def _cargar_sala(self, initial=False):
        sala = MAPA_ESCAPE[self.ubicacion_actual]
        titulo = f"[{a_mayusculas(self.ubicacion_actual)}]"
        self.lbl_titulo.config(text="ESCAPE ROOM DE CONOCIMIENTO   -   " + titulo)
        self.lbl_descripcion.config(text=sala['descripcion'])
        self._append_chat(f"Narrador: Entras en {self.ubicacion_actual}.")

        img = self.imagenes_cache.get(self.ubicacion_actual)
        if img is None:
            # placeholder
            self.canvas.delete("all")
            self.canvas.create_text(400,240, text="(Imagen no disponible)", fill="white", font=("Segoe UI", 18))
        else:
            # animación en hilo para no bloquear UI
            threading.Thread(target=self._animar_fade_slide, args=(img,)).start()

    def _animar_fade_slide(self, pil_img):
        steps = 14
        w, h = pil_img.size
        for i in range(steps):
            # fade factor
            alpha = (i+1)/steps
            enhancer = ImageEnhance.Brightness(pil_img)
            frame = enhancer.enhance(0.15 + 0.85*alpha)
            tk_img = ImageTk.PhotoImage(frame)
            # slide: calcular x desde -w -> 0 (centered)
            x = int(-w + (w+0)*(i+1)/steps)  # slide to 0 (we will anchor center via coords)
            # dibujar
            self.canvas.delete("all")
            # center: place at 0,0 with anchor nw after applying x
            self.canvas.create_image(x, 0, image=tk_img, anchor='nw')
            # mantener referencia
            self.canvas.image = tk_img
            time.sleep(0.03)
        # sonido de paso
        self._reproducir_sonido('paso')

    # ----- interacción: botones -----
    def _on_pista(self):
        sala = MAPA_ESCAPE[self.ubicacion_actual]
        prereq = sala.get('prerequisito','')
        if prereq and prereq not in self.inventario:
            messagebox.showinfo("Pista", f"Necesitas primero: {prereq} para ver más pistas.")
            self._append_chat("Sistema: Pista bloqueada por prerequisito.")
            self._reproducir_sonido('error')
            return
        # mostrar pista sutil
        pista = f"Pista: ({self._on_pista})."
        messagebox.showinfo("Pista", pista)
        self._append_chat("Sistema: Se mostró una pista.")
        self._reproducir_sonido('paso')

    def _on_enviar(self):
        entrada = self.entry.get().strip()
        self.entry.delete(0, 'end')
        if not entrada:
            return

        entrada_min = a_minusculas(entrada)
        if entrada_min == 'inventario':
            self._ventana_inventario()
            return
        if entrada_min == 'terminar':
            messagebox.showinfo("Salir", "Has terminado la partida.")
            self.root.destroy()
            return

        # usar validar_respuesta (misma firma)
        resultado = validar_respuesta(entrada, self.ubicacion_actual, self.inventario)

        if resultado == 'TERMINAR':
            # esto no ocurrirá aquí porque validar_respuesta en GUI devuelve True/False
            self.root.destroy()
            return

        if resultado:
            # tiene prerequisito (o ninguno) -> éxito
            data_sala = MAPA_ESCAPE[self.ubicacion_actual]
            recompensa = data_sala.get('recompensa')
            # añadir solo si no estaba
            if recompensa and recompensa not in self.inventario:
                self.inventario.append(recompensa)
                self._add_icono_inventario(recompensa)
                self._append_chat(f"Jugador: {entrada} -> Correcto. Recompensa obtenida: {recompensa}")
            else:
                self._append_chat(f"Jugador: {entrada} -> Correcto.")

            self._reproducir_sonido('correcto')

            # animación y cambio de sala en hilo
            siguiente = data_sala.get('siguiente_sala')
            threading.Thread(target=self._salto_sala_animado, args=(siguiente,)).start()

        else:
            # fallo: mostrar error (si falta prereq o respuesta incorrecta)
            # comprobamos si falla por prereq -> reutilizar tiene_prerequisito
            tiene, mensaje = tiene_prerequisito(self.ubicacion_actual, self.inventario)
            if not tiene:
                messagebox.showwarning("Requisito", mensaje)
                self._append_chat("Jugador: Intentó sin prerequisito.")
            else:
                messagebox.showerror("Incorrecto", MENSAJES_ERROR[2])
                self._append_chat("Jugador: Respuesta incorrecta.")
            self._reproducir_sonido('error')

    def _add_icono_inventario(self, clave):
        icon = self.iconos_cache.get(clave)
        frame = tk.Frame(self.frame_icons, bg="#071024", padx=4, pady=4)
        frame.pack(side='left')
        if icon:
            lbl = tk.Label(frame, image=icon, bg="#071024")
            lbl.image = icon
            lbl.pack()
        else:
            lbl = tk.Label(frame, text=clave, bg="#1e2430", fg="white", width=10, height=4)
            lbl.pack()
        tk.Label(frame, text=clave, bg="#071024", fg="white", font=("Segoe UI", 8)).pack()

    def _salto_sala_animado(self, siguiente_sala):
        # efecto slide-out (simple: oscurecer)
        for i in range(6):
            self.canvas.delete("all")
            alpha = 0.1 + i*0.15
            self.canvas.create_rectangle(0,0,800,480, fill="#000000", stipple="gray50", outline="")
            time.sleep(0.03)
        # cambiar
        self.ubicacion_actual = siguiente_sala
        if self.ubicacion_actual == 'Salida':
            self._append_chat("Sistema: ¡Has escapado con éxito!")
            messagebox.showinfo("Victoria", "¡HAS ESCAPADO CON ÉXITO!")
            # mostrar inventario final
            self._ventana_inventario()
            self.root.destroy()
            return
        # cargar nueva sala (fade+slide)
        self._cargar_sala()

    # ----- util -----
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

    def on_close(self):
        if messagebox.askokcancel("Salir", "¿Deseas salir del juego?"):
            self.root.destroy()

# ---------------------------
# Ejecución rápida (si se quiere correr en consola)
# ---------------------------

def main_console():
    mostrar_bienvenida_console()
    inventario = []
    ubicacion_actual = 'Biblioteca Antigua'

    while ubicacion_actual != 'Salida':
        data_sala = MAPA_ESCAPE[ubicacion_actual]
        print("[ESTÁS EN: " + a_mayusculas(ubicacion_actual) + "]")
        print(data_sala['descripcion'])
        tiene, mensaje_prereq = tiene_prerequisito(ubicacion_actual, inventario)
        if data_sala['prerequisito'] != "" and not tiene:
            print("AVISO: " + mensaje_prereq)
        entrada = input("Tu respuesta o comando > ")
        if a_minusculas(entrada) == 'inventario':
            mostrar_inventario_console(inventario)
            continue
        resultado_validacion = validar_respuesta(entrada, ubicacion_actual, inventario)
        if resultado_validacion == 'TERMINAR':
            break
        if resultado_validacion:
            recompensa = data_sala['recompensa']
            if recompensa not in inventario:
                inventario.append(recompensa)
                print("¡Recompensa obtenida! '" + recompensa + "' añadido al inventario.")
            input("Presiona ENTER para avanzar a la siguiente sala...")
            ubicacion_actual = data_sala['siguiente_sala']
    if ubicacion_actual == 'Salida':
        print("¡HAS ESCAPADO CON ÉXITO!")
        mostrar_inventario_console(inventario)

# ---------------------------
# Lanzador GUI
# ---------------------------

def main_gui():
    root = tk.Tk()
    app = EscapeRoomGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # Si prefieres consola, reemplaza por main_console()
    main_gui()
