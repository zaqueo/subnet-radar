# Subnet Radar

Herramienta web para escanear una red local mediante ping masivo en paralelo. Desarrollada para **Ixtanet**.

---

> ## Aviso Legal / Disclaimer
>
> Esta herramienta esta disenada exclusivamente para su uso en redes propias o redes sobre las cuales el usuario tiene autorizacion expresa del administrador o propietario.
>
> **El uso de esta herramienta sobre redes de terceros sin autorizacion puede constituir un delito informatico** segun la legislacion vigente en cada pais (acceso no autorizado a sistemas informaticos).
>
> El autor no se responsabiliza por el uso indebido de esta herramienta. El usuario asume toda la responsabilidad legal derivada de su uso.

---

## Caracteristicas

- Seleccion de mascara CIDR desde /16 hasta /30
- Escaneo en paralelo con 50 hilos simultaneos
- Estimacion de tiempo segun el tamano de la red
- Links directos a cada equipo detectado
- Compatible con Windows y Linux/macOS

---

## Requisitos

- Python 3.8 o superior
- pip

---

## Instalacion y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/zaqueo/subnet-radar.git
cd subnet-radar
```

### 2. Instalar dependencias

```bash
pip install flask
```

### 3. Lanzar la aplicacion

```bash
python app_escaner.py
```

### 4. Abrir en el navegador

Entra a: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Como usarlo

1. Ingresa la **direccion de red base** (ej: `192.168.1.0`)
2. Selecciona la **mascara CIDR** en el desplegable (ej: `/24` para 254 hosts)
3. La herramienta te muestra cuantas IPs se van a escanear y el tiempo estimado
4. Hace clic en **Escanear Red Ahora**
5. Los equipos activos apareceran como links directos a su interfaz web

> **Nota:** Para redes grandes (/20 o menor) el escaneo puede tardar varios minutos.
> Asegurate de estar conectado a la red local antes de escanear.

---

## Mascaras disponibles

| CIDR | Hosts | Tiempo estimado |
|------|-------|----------------|
| /30  | 2     | ~1 seg          |
| /28  | 14    | ~1 seg          |
| /24  | 254   | ~15 seg         |
| /22  | 1.022 | ~1 min          |
| /20  | 4.094 | ~4 min          |
| /16  | 65.534| ~65 min         |