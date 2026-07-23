import http.server
import socketserver
import urllib.request
import csv
import json
import io
import time
import os

PORT = int(os.environ.get("PORT", 8000))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/datos'):
            try:
                # 1. URL con timestamp (_t) para romper la caché de Google Sheets
                base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0vxe6GbEKkdwiHAHtg0pPBFO2aZqvo7Yki_ZSe0RxtDEeBHTYgRXzRgGhRHyUGfZZsNrDjHFmzDdu/pub?gid=0&single=true&output=csv"
                fresh_url = f"{base_url}&_t={int(time.time())}"

                req = urllib.request.Request(
                    fresh_url, 
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache'
                    }
                )

                with urllib.request.urlopen(req) as response:
                    csv_text = response.read().decode('utf-8')
                
                # 2. Convertir CSV a lista de diccionarios
                f = io.StringIO(csv_text)
                reader = csv.DictReader(f)
                filas = [row for row in reader]

                # 3. Enviar respuesta con encabezados estrictos que prohíben la caché
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                
                self.wfile.write(json.dumps(filas, ensure_ascii=False).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            super().do_GET()

print(f"Servidor corriendo en http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    httpd.serve_forever()