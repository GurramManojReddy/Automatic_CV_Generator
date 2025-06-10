from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import os

PORT = 8000

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/cv':
            params = urllib.parse.parse_qs(parsed.query)
            name = params.get('name', [''])[0]
            # Serve the one-time CV page
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = f'''
         <!DOCTYPE html>
         <html>
         <head><title>CV Ready</title></head>
         <body>
           <h2>Your CV is ready:</h2>
            <p>
            <a
              href="/CVs/current/{name}.pdf"
              target="_blank"
            >
              Open downloadedFile.pdf
            </a>
            </p>
           <p>File path: /Users/manoj/Desktop/Stunts/CVs/current/{name}.pdf</p>
           <script>
             // replace URL in address bar to home without reloading
             window.history.replaceState(null, null, '/');
           </script>
         </body>
         </html>
         '''
            self.wfile.write(html.encode())
            return

        elif parsed.path.startswith('/CVs/current/'):
            file_path = '.' + parsed.path  # Serves ./CVs/current/filename.pdf
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "File Not Found")
                return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = '''
<!DOCTYPE html>
<html>
<head>
  <title>Generate CV</title>
  <style>
    .container { display: flex; }
    .form-container { width: 50%; padding: 10px; }
    .table-container { width: 50%; padding: 10px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
  </style>
</head>
<body>
  <h2>Enter CV Details:</h2>
  <div class="container">
    <div class="form-container">
      <form method="POST">
        Full Name: <input type="text" name="full_name" required><br><br>
        Phone: <input type="text" name="phone" required><br><br>
        Email: <input type="email" name="email" required><br><br>
        CV Name: <input type="text" name="cv_name" required><br><br>
        Base Template Number(1 or 2): <input type="text" name="base" required><br><br>
        Projects (comma-separated indices e.g., 1,2,3,6,7): <input type="text" name="projects" required><br><br>
        <input type="submit" value="Generate CV">
      </form>
    </div>
    <div class="table-container">
      <h3>Project Reference Table</h3>
      <table>
        <tr><th>Key</th><th>Description</th><th>Keywords</th></tr>
        <tr><td>1</td><td>Meal Nutrition Analysis</td><td>PyTorch, Pandas, NumPy, OpenCV, CNN, Multimodal</td></tr>
        <tr><td>2</td><td>Local Search Engine</td><td>Python, Streamlit, FAISS, BM25, LLMs</td></tr>
        <tr><td>3</td><td>Leadership Effectiveness Inventory</td><td>Ruby, Rails, Agile, Git, JavaScript, Postgres, SQL</td></tr>
        <tr><td>4</td><td>Operating Systems Kernel From Scratch</td><td>C, C++, Assembly, Shell</td></tr>
        <tr><td>5</td><td>Portfolio Management</td><td>R, Python, NLP, IBrokers, Transformers, BERT</td></tr>
        <tr><td>6</td><td>Task Tracker Web Suite</td><td>Angular, Java, Spring Boot, REST API, Bootstrap</td></tr>
        <tr><td>7</td><td>BMI Calculator</td><td>Flutter, Dart, Material Design</td></tr>
        <tr><td>8</td><td>RL-Based Dynamic Thermal Management</td><td>Python, Arduino, Linux, PPO</td></tr>
        <tr><td>9</td><td>Secure Blog Platform</td><td>React, Node.js, Express, MongoDB, REST, JWT</td></tr>
      </table>
    </div>
  </div>
</body>
</html>
'''
        self.wfile.write(html.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(post_data)

        try:
            phone = data['phone'][0]
            email = data['email'][0]
            name = data['cv_name'][0]
            full_name = data['full_name'][0]
            base = data['base'][0]
            projects = [p.strip() for p in data['projects'][0].split(',')]

            json_data = {
                "phone": phone,
                "email": email,
                "name": name,
                "full_name": full_name,
                "base": base,
                "projects": projects
            }

            with open("var.json", "w") as f:
                import json
                json.dump(json_data, f)
            print("Generating Latex")
            # Ensure the script is executable and run it from the current working directory
            script_path = "/Users/manoj/Desktop/Stunts/run_editor.sh"
            subprocess.run(
                ["bash", script_path],
                cwd=os.getcwd(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            print("Latex Generated")
            self.send_response(303)
            self.send_header('Location', f'/cv?name={name}')
            self.end_headers()
        except Exception as e:
            download_link = f"Error: {e}"
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(download_link.encode())

if __name__ == '__main__':
    print(f"Serving on http://localhost:{PORT}")
    with HTTPServer(("", PORT), SimpleHandler) as server:
        server.serve_forever()