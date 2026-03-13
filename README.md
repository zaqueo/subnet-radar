# Subnet Radar

Herramienta web para escanear subnets remotas mediante ping masivo. Desarrollada para **Ixtanet**.

## Características

- Escaneo de hasta 254 IPs en paralelo (50 hilos)
- Interfaz web moderna con Bootstrap 5
- Links directos a cada equipo detectado
- Compatible con Windows y Linux

## Instalación

```bash
pip install flask
```

## Uso

```bash
python app_escaner.py
```

Luego abre tu navegador en: [http://127.0.0.1:5000](http://127.0.0.1:5000)

Ingresá el rango de red (ej: `100.100.100.0/24`) y hacé clic en **Escanear Red Ahora**.
