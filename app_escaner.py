from flask import Flask, render_template_string, jsonify, request
import platform
import subprocess
import concurrent.futures
import ipaddress

app = Flask(__name__)

# --- INTERFAZ HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ixtanet - Escáner de Red</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #0d6efd; /* Azul tecnológico */ }
        .card { box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-radius: 12px; border: none; }
        .badge-activo { background-color: #ff8c00; /* Naranja para contraste */ }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark mb-5 shadow-sm">
        <div class="container">
            <span class="navbar-brand mb-0 h1 fw-bold">Herramientas de Red - Ixtanet</span>
        </div>
    </nav>
    
    <div class="container">
        <div class="card p-4 mx-auto" style="max-width: 600px;">
            <h4 class="text-center mb-4 text-secondary">Escáner de Subred Remota</h4>
            
            <div class="mb-4">
                <label for="subred" class="form-label fw-bold">Rango IP / Subred:</label>
                <input type="text" class="form-control form-control-lg text-center" id="subred" value="100.100.100.0/24">
            </div>
            
            <button id="btnEscanear" class="btn btn-primary btn-lg w-100 mb-4" onclick="iniciarEscaneo()">
                Escanear Red Ahora
            </button>
            
            <div id="loading" class="text-center d-none mb-4">
                <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
                <p class="mt-3 text-muted fw-bold">Haciendo ping a 254 IPs, por favor espera...</p>
            </div>

            <ul id="resultados" class="list-group list-group-flush">
                </ul>
        </div>
    </div>

    <script>
        async function iniciarEscaneo() {
            const subred = document.getElementById('subred').value;
            const btn = document.getElementById('btnEscanear');
            const loading = document.getElementById('loading');
            const resultados = document.getElementById('resultados');

            // Bloquear botón y mostrar spinner
            btn.disabled = true;
            loading.classList.remove('d-none');
            resultados.innerHTML = '';

            try {
                // Hacer la petición a nuestro servidor Python
                const response = await fetch('/escanear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ subred: subred })
                });
                
                const data = await response.json();
                
                // Mostrar resultados
                if (data.ips.length === 0) {
                    resultados.innerHTML = '<li class="list-group-item text-danger text-center fw-bold">No se encontraron equipos activos o no hay respuesta del túnel.</li>';
                } else {
                    data.ips.forEach(ip => {
                        let link = `<a href="http://${ip}" target="_blank" class="text-decoration-none text-dark">${ip}</a>`;
                        resultados.innerHTML += `
                        <li class="list-group-item d-flex justify-content-between align-items-center fs-5">
                            ${link}
                            <span class="badge badge-activo rounded-pill">Detectado</span>
                        </li>`;
                    });
                }
            } catch (error) {
                resultados.innerHTML = '<li class="list-group-item text-danger text-center">Error de conexión con el servidor local.</li>';
            } finally {
                // Restaurar botón y ocultar spinner
                btn.disabled = false;
                loading.classList.add('d-none');
            }
        }
    </script>
</body>
</html>
"""

# --- LÓGICA DEL MOTOR PING ---
def hacer_ping(ip_str):
    # Detectar el sistema operativo para adaptar los comandos de consola
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    param_timeout = '-w' if platform.system().lower() == 'windows' else '-W'
    val_timeout = '1000' if platform.system().lower() == 'windows' else '1'
    
    comando = ['ping', parametro, '1', param_timeout, val_timeout, ip_str]
    try:
        salida = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        if salida.returncode == 0:
            return ip_str, True
    except subprocess.TimeoutExpired:
        pass
    return ip_str, False

# --- RUTAS DE FLASK ---
@app.route('/')
def index():
    # Sirve la página HTML cuando entras al navegador
    return render_template_string(HTML_TEMPLATE)

@app.route('/escanear', methods=['POST'])
def escanear():
    # Recibe la subred desde el HTML y ejecuta el escaneo
    datos = request.get_json()
    subred = datos.get('subred', '100.100.100.0/24')
    
    ips_activas = []
    try:
        red = ipaddress.IPv4Network(subred, strict=False)
        ips_a_escanear = [str(ip) for ip in red.hosts()]
        
        # 50 hilos para escanear rapidísimo
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ejecutor:
            resultados = ejecutor.map(hacer_ping, ips_a_escanear)
            for ip, activa in resultados:
                if activa:
                    ips_activas.append(ip)
    except ValueError:
        return jsonify({'error': 'Subred inválida'}), 400
        
    return jsonify({'ips': ips_activas})

if __name__ == '__main__':
    # Inicia el servidor en el puerto 5000
    print("Servidor web iniciado.")
    print("Abre tu navegador y entra a: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)