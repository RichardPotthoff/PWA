import base64
from PIL import Image
import io
import json
import os

# Step 1: Create a simple icon (a 192x192 red square)
icon_size = (192, 192)
icon = Image.new("RGB", icon_size, color="red")  # Create a red square
icon_buffer = io.BytesIO()
icon.save(icon_buffer, format="PNG")
icon_data = icon_buffer.getvalue()
icon_base64 = base64.b64encode(icon_data).decode("utf-8")

# Step 2: Create the PWA manifest as a dictionary
manifest = {
    "name": "Simple PWA Counter",
    "short_name": "PWA Counter",
    "start_url": "/",
    "display": "standalone",  # Enables full-screen mode
    "background_color": "#ffffff",
    "theme_color": "#ff0000",
    "icons": [
        {
            "src": f"data:image/png;base64,{icon_base64}",
            "sizes": "192x192",
            "type": "image/png"
        }
    ]
}
manifest_json = json.dumps(manifest)
manifest_base64 = base64.b64encode(manifest_json.encode("utf-8")).decode("utf-8")

# Step 3: Create the HTML content with embedded manifest, icon, and Service Worker
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple PWA Counter</title>

    <!-- iOS PWA Meta Tags for Full-Screen Mode -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="PWA Counter">

    <!-- Embed the PWA Manifest Inline -->
    <link rel="manifest" href="data:application/manifest+json;base64,{manifest_base64}">

    <!-- Basic CSS for Styling -->
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
            background-color: #f0f0f0;
        }}
        button {{
            padding: 10px 20px;
            font-size: 16px;
            margin: 5px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #cc0000;
        }}
        #counter {{
            font-size: 24px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>Simple PWA Counter</h1>
    <div id="counter">0</div>
    <button onclick="incrementCounter()">Increment</button>
    <button onclick="decrementCounter()">Decrement</button>

    <script>
        // Counter logic
        let count = 0;
        const counterElement = document.getElementById("counter");

        function incrementCounter() {{
            count++;
            counterElement.innerText = count;
        }}

        function decrementCounter() {{
            count--;
            counterElement.innerText = count;
        }}

        // Register the Service Worker (embedded inline)
        const swCode = `
            const CACHE_NAME = 'pwa-counter-cache-v1';
            const urlsToCache = ['/'];

            self.addEventListener('install', event => {{
                event.waitUntil(
                    caches.open(CACHE_NAME)
                        .then(cache => {{
                            console.log('Caching resources');
                            return cache.addAll(urlsToCache);
                        }})
                );
            }});

            self.addEventListener('fetch', event => {{
                event.respondWith(
                    caches.match(event.request)
                        .then(response => {{
                            if (response) {{
                                return response;
                            }}
                            return fetch(event.request);
                        }})
                );
            }});

            self.addEventListener('activate', event => {{
                const cacheWhitelist = [CACHE_NAME];
                event.waitUntil(
                    caches.keys().then(cacheNames => {{
                        return Promise.all(
                            cacheNames.map(cacheName => {{
                                if (!cacheWhitelist.includes(cacheName)) {{
                                    return caches.delete(cacheName);
                                }}
                            }})
                        );
                    }})
                );
            }});
        `;

        // Create a Blob for the Service Worker and register it
        const swBlob = new Blob([swCode], {{ type: 'application/javascript' }});
        const swUrl = URL.createObjectURL(swBlob);

        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register(swUrl)
                .then(reg => console.log('Service Worker registered', reg))
                .catch(err => console.error('Service Worker registration failed', err));
        }}
    </script>
</body>
</html>
"""

# Step 4: Write the HTML file to disk in Pythonista
# Pythonista stores files in its own sandboxed directory
#output_path = os.path.expanduser("~/Documents/pwa_counter.html")
output_path="pwa_counter.html"
with open(output_path, "w") as f:
    f.write(html_content)

print(f"HTML file written to: {output_path}")
