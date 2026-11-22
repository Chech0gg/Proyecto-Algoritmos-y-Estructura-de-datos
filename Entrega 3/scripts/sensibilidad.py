import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitorias import prioridad


def pedidos(n, semilla):
    random.seed(semilla)
    resultado = []
    for i in range(n):
        maximo = 8
        resultado.append({"id": i, "nota": random.uniform(0, 5), "dependientes": random.randint(0, maximo),
                          "maximo": maximo, "llegada": random.uniform(0, 14)})
    return resultado


def orden(lista, ancho, dias):
    claves = {}
    for p in lista:
        r = prioridad.riesgo(p["nota"], ancho=ancho)
        u = prioridad.urgencia(r, prioridad.impacto(p["dependientes"], p["maximo"]))
        claves[p["id"]] = prioridad.clave_cola(u, p["llegada"], dias)
    return sorted(claves, key=lambda i: (claves[i], i))


def tau_kendall(a, b):
    posicion = {v: i for i, v in enumerate(b)}
    concordantes = 0
    discordantes = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if posicion[a[i]] < posicion[a[j]]:
                concordantes += 1
            else:
                discordantes += 1
    return (concordantes - discordantes) / (concordantes + discordantes)


def main():
    lista = pedidos(200, 2026)
    base = orden(lista, prioridad.ancho_riesgo, prioridad.dias_envejecimiento)
    print("sensibilidad del orden de la cola frente a los parametros (200 solicitudes sinteticas)")
    print("base: ancho = 1.0 (anclas 10 % / 50 % / 90 %), t = 7 dias")
    print(f"{'ancho':>6} {'t (dias)':>9} {'tau de kendall':>15} {'coincidencia en el top 20':>26}")
    for ancho in (0.5, 0.75, 1.0, 1.5, 2.0):
        for dias in (3.0, 7.0, 14.0):
            variante = orden(lista, ancho, dias)
            tau = tau_kendall(base, variante)
            coincidencia = len(set(base[:20]) & set(variante[:20]))
            marca = "  <- base" if ancho == 1.0 and dias == 7.0 else ""
            print(f"{ancho:>6} {dias:>9} {tau:>15.3f} {coincidencia:>22}/20{marca}")


if __name__ == "__main__":
    main()
