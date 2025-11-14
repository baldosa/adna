import os
import time
import random
from collections import Counter


# limpio la pantalla
def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# colores y tipos de cartas
COLORES = ["marrón", "naranja", "rosa", "violeta"]
VALORES_NUMERICOS = list(range(1, 10))  # Del 1 al 9
TIPOS_ACCION = [
    "Toma 2",
    "Reversa",
    "Salta",
    "Toma 4",
]


class Carta:
    """
    Representa una carta individual del juego.
    """

    def __init__(self, color, valor):
        self.color = color
        self.valor = valor  # Puede ser un número (1-9) o un tipo de acción

    def __str__(self):
        # Dice valor y color
        return f"{self.valor} {self.color}"

    def es_accion(self):
        # chequea si el valor está en los tipos de acción
        return self.valor in TIPOS_ACCION

    def es_numerica(self):
        # isinstance valida el tipo de valor de la variable
        return isinstance(self.valor, int)


class Mazo:
    """
    Representa el Mazo y el Pozo.
    """

    def __init__(self):
        self.cartas = []
        self.pozo = []
        self.crear_mazo()
        self.mezclar()

    def crear_mazo(self):
        """
        Crea el mazo de 100 cartas según las reglas
        """
        self.cartas = []

        for color in COLORES:
            # 72 cartas numéricas
            for valor in VALORES_NUMERICOS:
                self.cartas.append(Carta(color, valor))
                self.cartas.append(Carta(color, valor))

            # 28 cartas de acción
            # 8 "Toma Dos"
            self.cartas.append(Carta(color, "Toma 2"))
            self.cartas.append(Carta(color, "Toma 2"))

            # 8 "Reversa"
            self.cartas.append(Carta(color, "Reversa"))
            self.cartas.append(Carta(color, "Reversa"))

            # 8 "Salta"
            self.cartas.append(Carta(color, "Salta"))
            self.cartas.append(Carta(color, "Salta"))

            # 4 "Toma Cuatro"
            self.cartas.append(Carta(color, "Toma 4"))

    def mezclar(self):
        # usa random.shuffle que mezcla la lista en el lugar
        random.shuffle(self.cartas)

    def sacar_carta(self):
        """
        Saca una carta del tope del mazo.
        Maneja el coso de cuando el mazo se termina y comienza de nuevo
        """
        if not self.cartas:
            print("Mezclando el pozo...")
            self.regenerar_mazo()

            # no hay cartas ni en el pozo para regenerar
            if not self.cartas:
                print("no hay más cartas en juego! no ganó nadie...")
                return None

        return self.cartas.pop()

    def regenerar_mazo(self):
        """
        Mantengo la última carta como pozo, repopulo el mazo y lo mezclo
        """
        # La carta superior del pozo se queda
        carta_tope = self.pozo.pop()
        self.cartas = self.pozo

        # renuevo el pozo con la carta topa
        self.pozo = [carta_tope]

        # mezclo el nuevo mazo
        self.mezclar()

    def iniciar_pozo(self):
        """
        Inicio el pozo, doy vueltas cartas hasta que sea numérica
        """
        carta = self.sacar_carta()
        while carta.es_accion():
            print(f"Salió una carta de acción ({carta}). Agarrando la siguiente...")
            self.pozo.append(carta)  # Se pone en el pozo igualmente
            carta = self.sacar_carta()

        self.pozo.append(carta)
        print(f"El pozo inicia con: {self.ver_tope_pozo()}")

    def ver_tope_pozo(self):
        return self.pozo[-1] if self.pozo else None

    def agregar_al_pozo(self, carta):
        self.pozo.append(carta)


class Jugador:
    """
    Clase base para todos los jugadores.
    """

    def __init__(self, nombre):
        self.nombre = nombre
        self.mano = []
        self.dijo_adna = False

    def tomar_cartas_del_mazo(self, mazo, cantidad=1):
        print(f"{self.nombre} toma {cantidad} carta(s).")
        for i in range(cantidad):
            carta = mazo.sacar_carta()
            if carta:
                self.mano.append(carta)
            else:
                break
        self.dijo_adna = False  # Si agarra cartas, no va a tener adná

    def jugar_carta(self, carta_idx, mazo):
        """
        Juega carta de la mano al pozo
        """
        carta = self.mano.pop(carta_idx)
        mazo.agregar_al_pozo(carta)
        print(f"{self.nombre} juega: {carta}")

    def decir_adna(self):
        print(f"Adná!")
        self.dijo_adna = True

    def mostrar_mano(self):
        print(f"\n--- Mano de {self.nombre} ---")
        for i, carta in enumerate(self.mano):
            print(f"  {i+1}: {carta}")
        print("------------------------")

    def __str__(self):
        # Es como mirar al jugar y contar sus cartas
        return f"Jugador {self.nombre} (Cartas: {len(self.mano)})"


class JugadorHumano(Jugador):
    """
    Jugadores Humanos.
    """

    def __init__(self, nombre):
        super().__init__(nombre)
        self.es_humano = True

    def mostrar_mano(self):
        print(f"\n--- Mano de {self.nombre} ---")
        for i, carta in enumerate(self.mano):
            print(f"  {i+1}: {carta}")
        print("------------------------")

    def jugar(self, juego):
        """
        Lógica para que el humano elija qué hacer
        """
        self.mostrar_mano()
        print(f"Tope del pozo: {juego.mazo.ver_tope_pozo()}")

        if juego.mazo.ver_tope_pozo().valor in TIPOS_ACCION and juego.accion_pendiente:
            # chequeo si el jugador tiene cartas de acción para continuar la acumulación
            if not juego.mazo.ver_tope_pozo().valor in [
                carta.valor for carta in self.mano
            ]:
                # Si el jugador no tiene cartas de acción, debe cumplir penalidad
                print(
                    f"{self.nombre} tiene que cumplir penalidad del pozo por {juego.mazo.ver_tope_pozo()}."
                )
                self.tomar_cartas_del_mazo(juego.mazo, juego.cartas_acumuladas)
                juego.cartas_acumuladas = 0
                juego.accion_pendiente = None
                input("Presiona una tecla para continuar...")
                return None
            else:
                print(f"{self.nombre} puede jugar una carta para continuar acumulación")

        print("Opciones:")
        print("  1. Jugar una carta (ingrese el número de la carta)")
        print("  2. Jugar carta y decir '¡Adná!'")
        print("  3. Tomar una carta del mazo")

        # decision = 2
        decision = int(input("¿Qué hacés? "))
        match decision:
            case 1:
                # Jugar carta
                carta_idx = int(input("Ingrese el número de la carta a jugar: ")) - 1
                carta_a_jugar = self.mano[carta_idx]

                if juego.es_jugada_valida(carta_a_jugar, juego.mazo.ver_tope_pozo()):
                    self.jugar_carta(carta_idx, juego.mazo)
                    return carta_a_jugar
                else:
                    print("Jugada inválida. Tomando carta en su lugar.")
                    # si la jugada es invlaida y hay accion pendiente quiere decir que quiso "engañar"
                    # al juego por lo que tiene que agarrar las cartas acumuladas, sino hay accion pendiente
                    # agarra 1 como si solo hubiera elegido "tomar carta"
                    cartas_a_agarrar = (
                        juego.cartas_acumuladas if juego.accion_pendiente else 1
                    )
                    self.tomar_cartas_del_mazo(juego.mazo, cartas_a_agarrar)
                    return None
                return carta_a_jugar
            case 2 if len(self.mano) == 2:
                # Jugar carta y decir adná
                carta_idx = int(input("Ingrese el número de la carta a jugar: ")) - 1
                carta_a_jugar = self.mano[carta_idx]
                if juego.es_jugada_valida(carta_a_jugar, juego.mazo.ver_tope_pozo()):
                    self.jugar_carta(carta_idx, juego.mazo)
                    self.dijo_adna = True
                    return carta_a_jugar
                else:
                    print("Jugada inválida. Tomando carta en su lugar.")
                    # si la jugada es invlaida y hay accion pendiente quiere decir que quiso "engañar"
                    # al juego por lo que tiene que agarrar las cartas acumuladas, sino hay accion pendiente
                    # agarra 1 como si solo hubiera elegido "tomar carta"
                    cartas_a_agarrar = (
                        juego.cartas_acumuladas if juego.accion_pendiente else 1
                    )
                    self.tomar_cartas_del_mazo(juego.mazo, cartas_a_agarrar)
                    return None
            case 3:
                # Tomar carta
                self.tomar_cartas_del_mazo(juego.mazo, 1)
                return None


class JugadorBotB(Jugador):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.es_humano = False

    def jugar(self, juego):
        """
        Estrategia "Agresiva":
        1. Prioriza "atacar" jugando cartas de acción
            a. Responde a carta de ataque
            b. Jugar cartas de "Toma" (Toma Cuatro, Toma Dos)
            c. Jugar "Salta" o "Reversa"
        2. Jugar numéricas, intentando cambiar a un color que C "no tenga". Usando el Pozo para inferir qué colores son "raros"
        """

        carta_pozo = juego.mazo.ver_tope_pozo()
        pozo_completo = juego.mazo.pozo
        jugadas_validas = []
        for carta in self.mano:
            if juego.es_jugada_valida(carta, carta_pozo):
                jugadas_validas.append(carta)

        # donde guardo las acumulaciones
        acumulables = []
        # donde voy a guardar las cartas de acción en el orden deseado
        accion = []
        # guardo las numéricas para el SINO
        numericas = []

        carta_a_jugar = None

        # Clasificar las cartas jugables
        for carta in jugadas_validas:
            # 1. Prioridad Acumular
            if carta.valor == juego.mazo.ver_tope_pozo().valor and carta.es_accion():
                acumulables.append(carta)
            # 2. Prioridad Cartas de Toma
            elif carta.valor == "Toma 4":
                accion.append(carta)
            elif carta.valor == "Toma 2":
                accion.append(carta)
            # 3. Prioridad Salta/Reversa
            elif carta.valor in ["Salta", "Reversa"]:
                accion.append(carta)
            # 4. Cartas numéricas
            elif carta.es_numerica():
                numericas.append(carta)

        # --- Tomar Decisión (Orden de Prioridad) ---

        if acumulables:
            # Prioridad 1: Siempre acumular o jugar acción.
            carta_a_jugar = acumulables[0]
        if accion:
            carta_a_jugar = accion[0]  # Prioridad 1: Siempre acumular o jugar acción.

        elif numericas:
            # cuenta qué colores han salido MENOS en el pozo.
            # La estrategia es jugar uno de esos colores "raros",
            # asumiendo que el siguiente jugador tiene menos probabilidad de tenerlo.
            conteo_colores_pozo = Counter(c.color for c in pozo_completo)

            # Ordena las cartas numéricas jugables, prefiriendo las de colores
            # que han aparecido MENOS veces en el pozo.
            numericas.sort(key=lambda c: conteo_colores_pozo[c.color])
            carta_a_jugar = numericas[0]
        elif jugadas_validas:
            carta_a_jugar = jugadas_validas[0]

        if not acumulables and juego.mazo.ver_tope_pozo().es_accion():
            print("Bot B no puede jugar, cumple penalidad")
            self.tomar_cartas_del_mazo(juego.mazo, juego.cartas_acumuladas)
            juego.cartas_acumuladas = 0
            juego.accion_pendiente = None
        elif carta_a_jugar:
            # Juega la carta seleccionada
            carta_idx = self.mano.index(carta_a_jugar)
            self.jugar_carta(carta_idx, juego.mazo)
            print(f"Bot D: Jugando carta {carta_a_jugar}")
            if len(self.mano) == 1:
                print("Bot D dice Adná!")
                self.dijo_adna = True
            return carta_a_jugar
        else:
            print(f"Bot B: no puedo hacer nada, tomo carta")
            self.tomar_cartas_del_mazo(juego.mazo, 1)
            return None


class JugadorBotD(Jugador):
    def __init__(self, nombre):
        super().__init__(nombre)
        self.es_humano = False

    def jugar(self, juego):
        """
        Estrategia "conservadora":
        1. Juega acciones solo para responder a acciones Toma 2 y Toma 4
        2. Prioriza jugar cartas numéricas. Usa el pozo para seleccionar que numero/color jugar
        3. Guardar cartas de acción (Toma, Salta, Reversa) para jugar a lo último y solo las juega si no queda otra
        """

        carta_pozo = juego.mazo.ver_tope_pozo()
        pozo_completo = juego.mazo.pozo
        jugadas_validas = []
        for carta in self.mano:
            if juego.es_jugada_valida(carta, carta_pozo):
                jugadas_validas.append(carta)

        # --- Listas de Prioridades ---
        acumulables = []
        numericas = []
        otras_acciones = []  # saltar y reversa
        carta_a_jugar = None

        for carta in jugadas_validas:
            # 1. Prioridad Acumular (Defensivo)
            if carta.valor == juego.mazo.ver_tope_pozo().valor and carta.es_accion():
                acumulables.append(carta)
            # 2. Prioridad Cartas Numéricas
            elif carta.es_numerica():
                numericas.append(carta)
            else:
                otras_acciones.append(carta)

        # --- Decisión por prioridad ---
        if acumulables:
            print(f"Bot D: Defendiendo/Acumulando con {acumulables[0]}")
            carta_a_jugar = acumulables[0]  # Prioridad 1: Siempre defenderse.

        elif numericas:
            # Contar qué colores y números hay en mi PROPIA mano.
            conteo_colores_mano = Counter(c.color for c in self.mano)

            # La estrategia es jugar una carta de un color que TENGO MUCHO.
            # ¿Por qué? Maximiza las chances de poder jugar en el futuro
            # si la ronda vuelve al mismo color.
            # Ordena las cartas numéricas, prefiriendo las de colores
            # que tiene MÁS en su mano.
            numericas.sort(key=lambda c: conteo_colores_mano[c.color], reverse=True)

            print(f"Bot D: Jugando numérica (optimizando mano) {numericas[0]}")
            carta_a_jugar = numericas[0]

        elif otras_acciones:
            # Último recurso: jugar una carta de acción (ej. un "Salta" sobre un 5)
            # Ordena jugar primero las que no son "Toma"
            otras_acciones.sort(
                key=lambda c: c.valor == "Toma 2" or c.valor == "Toma 4"
            )
            print(f"Bot D: Jugando acción (último recurso) {otras_acciones[0]}")
            carta_a_jugar = otras_acciones[0]
        elif jugadas_validas:
            print("Bot D: juego cualquier cosa válida")
            carta_a_jugar = jugadas_validas[0]

        if not acumulables and juego.mazo.ver_tope_pozo().es_accion():
            print("Bot D no puede jugar, cumple penalidad")
            self.tomar_cartas_del_mazo(juego.mazo, juego.cartas_acumuladas)
            juego.cartas_acumuladas = 0
            juego.accion_pendiente = None
        if carta_a_jugar:
            # Juega la carta seleccionada
            carta_idx = self.mano.index(carta_a_jugar)
            self.jugar_carta(carta_idx, juego.mazo)
            print(f"Bot D: Jugando carta {carta_a_jugar}")
            if len(self.mano) == 1:
                print("Bot D dice Adná!")
                self.dijo_adna = True
            return carta_a_jugar
        else:
            print("Bot D: no puedo hacer nada, tomo carta")
            self.tomar_cartas_del_mazo(juego.mazo, 1)
            return None


class Juego:
    """
    Controla todo el flujo de la partida.
    """

    def __init__(self):
        self.mazo = Mazo()
        self.jugadores = [
            JugadorHumano("A"),  #
            JugadorBotB("B"),  #
            JugadorHumano("C"),  #
            JugadorBotD("D"),  #
        ]
        self.jugador_actual_idx = 0
        self.direccion = 1  # 1 para A->B->C->D, -1 para A->D->C->B
        self.turno_activo = True

        # Variables para acumulación de acciones
        self.cartas_acumuladas = 0
        self.accion_pendiente = None  # "TomaDos", "TomaCuatro"

    def repartir_inicial(self):
        """
        Reparte 5 cartas a cada jugador en orden
        """
        # cambiar cartas para probar con menos
        cartas = 5
        for i in range(cartas):
            for jugador in self.jugadores:
                jugador.tomar_cartas_del_mazo(self.mazo, 1)

    def iniciar_juego(self):
        print("Iniciando partida de ADNA!")
        self.mazo.iniciar_pozo()
        self.repartir_inicial()
        self.jugador_actual_idx = 0  # Comienza A
        # TODO
        # ver si comienzo acá o en __main__
        self.jugar_ronda()

    def mostrar_juego(self):
        """
        Muestra el estado constante del juego
        """

        print("=============================")
        print(f"Tope del Pozo: {self.mazo.ver_tope_pozo()}")
        print(f"Cartas en el Mazo: {len(self.mazo.cartas)}")
        print("--- Manos (Humanos) ---")
        jugadores_humanos = [j for j in self.jugadores if j.es_humano]
        for jugador in jugadores_humanos:
            print(f"  {jugador.nombre}: {len(jugador.mano)} cartas")
            jugador.mostrar_mano()
        print("--- Estado (Robots) ---")
        jugadores_robots = [j for j in self.jugadores if not j.es_humano]
        for jugador in jugadores_robots:
            print(f"  {jugador.nombre}: {len(jugador.mano)} cartas")
            # DESCOMENTAR PARA DEBUG Y MOSTRAR LA MANO DEL
            # jugador.mostrar_mano()
        print("=============================")

    def penalidad_adna(self, jugador):
        """
        Penalidad por no decir "adná" al ganar
        """
        print(f"¡{jugador.nombre} no dijo 'Adná!'! Penalidad.")
        jugador.tomar_cartas_del_mazo(self.mazo, 2)
        jugador.dijo_adna = False
        input("Presione una tecla para continuar...")

    def avanzar_turno(self):
        """
        Pasa al siguiente jugador según la dirección.
        """
        self.jugador_actual_idx = (self.jugador_actual_idx + self.direccion) % 4
        self.turno_activo = True  # El nuevo jugador tiene un turno activo

    def es_jugada_valida(self, carta, carta_tope_pozo):
        # Lógica de validación
        if carta.color == carta_tope_pozo.color:
            return True
        if (
            carta.es_numerica()
            and carta_tope_pozo.es_numerica()
            and carta.valor == carta_tope_pozo.valor
        ):
            return True
        if (
            carta.es_accion()
            and carta_tope_pozo.es_accion()
            and carta.valor == carta_tope_pozo.valor
        ):
            return True
        return False

    def procesar_accion(self, carta):
        """
        Procesa los efectos de las cartas de acción
        """
        if not carta:
            # El jugador tomó carta, no hay acción que procesar
            return

        if carta.valor == "Reversa":
            self.direccion *= -1
            print(f"¡Cambia el sentido! Nueva dirección: {self.direccion}")

        elif carta.valor == "Salta":
            self.avanzar_turno()  # Salta al siguiente
            print(
                f"¡Salta! {self.jugadores[self.jugador_actual_idx].nombre} pierde el turno."
            )

        elif carta.valor == "Toma 2":
            self.cartas_acumuladas += 2
            self.accion_pendiente = "Toma 2"
            print(
                f"¡Acumulación! Próximo jugador debe tomar {self.cartas_acumuladas} cartas o jugar otro 'Toma 2'."
            )

        elif carta.valor == "Toma 4":
            self.cartas_acumuladas += 4
            self.accion_pendiente = "Toma 4"
            print(
                f"¡Acumulación! Próximo jugador debe tomar {self.cartas_acumuladas} cartas o jugar otro 'Toma 4'."
            )

    def verificar_ganador(self, jugador):
        if len(jugador.mano) == 0:
            if jugador.es_humano and not jugador.dijo_adna:
                # No dijo adná y ganó
                self.penalidad_adna(jugador)
                return False
            else:
                # Ganó
                print(f"\n¡¡¡ {jugador.nombre} ha ganado la partida !!!")
                return True
        return False

    def jugar_ronda(self):
        """
        Ejecuta un turno completo.
        """
        # COMENTAR PARA DEBUG Y NO BORRAR LA PANTALLA
        clear_screen()
        while True:  # Bucle principal del juego
            jugador = self.jugadores[self.jugador_actual_idx]

            # si no dijo ADNA, lo penalizo y paso al siguiente
            if len(jugador.mano) == 1 and not jugador.dijo_adna:
                self.penalidad_adna(jugador)
                self.turno_activo = False

            # Turno activo y sus cosas
            if self.turno_activo:
                print(f"\n--- Turno de {jugador.nombre} ---")

                # Mostrar estado (solo si es humano, o siempre?)
                # La consigna dice "constantemente"
                if jugador.es_humano:
                    self.mostrar_juego()

                elif not jugador.es_humano:
                    print("Jugar robot")

                # El jugador decide (sea humano o robot)
                carta_jugada = jugador.jugar(self)

                if self.verificar_ganador(jugador):
                    break  # Termina el juego

                # Procesar la acción de la carta (si se jugó una)
                self.procesar_accion(carta_jugada)

            # Pasar al siguiente turno
            self.avanzar_turno()


if __name__ == "__main__":
    juego = Juego()
    juego.iniciar_juego()
