import sys
import json
import re
import shutil
import subprocess
import os

def update_latex():
    try:
        # Ensure directories exist
        os.makedirs("CVs/current", exist_ok=True)
        # Load variables from var.json
        with open("var.json", "r") as json_file:
            data = json.load(json_file)
        phone = data['phone']
        email = data['email']
        full_name = data['full_name']

        # Choose base file based on input
        base_map = {"1": "base1.tex", "2": "base2.tex"}
        base_key = str(data.get("base", "1"))
        base_file = base_map.get(base_key, "base1.tex")
        with open(base_file, "r") as f:
            content = f.read()

        content = content.replace("945-276-9919", phone)
        content = content.replace("gurrammanojreddy850@gmail.com", email)
        content = content.replace("Manoj Reddy Gurram", full_name)

        # Insert project entries into the Projects section
        project_entries = []
        for i in data.get('projects', []):
            try:
                with open(f"projects/{i}.txt", "r") as pf:
                    project_entries.append(pf.read().strip())
            except FileNotFoundError:
                continue

        # Find the Projects section and inject entries
        pattern = r"(\\section\{Projects\}\s*\\resumeSubHeadingListStart)(.*?)(\\resumeSubHeadingListEnd)"
        replacement = lambda m: f"{m.group(1)}\n" + "\n\n".join(project_entries) + f"\n{m.group(3)}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)


        # Write to temp.tex
        with open("temp.tex", "w") as f:
            f.write(content)

        # Compile using pdflatex
        try:
            subprocess.run(
                ["pdflatex", "temp.tex"],
                input=b"\n\n",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except Exception as e:
            pass
        # After generating new PDF, rename it based on the name from var.json
        name = data.get("name", "temp")
        # print(f'{name}')
        # if os.path.exists("temp.pdf"):
        #     os.rename("temp.pdf", f"{name}.pdf")
        # else:
        #     raise FileNotFoundError("PDF generation failed: temp.pdf not found")

        # Move existing .pdf files from CVs/current/ to CVs/ without renaming them
        for file in os.listdir("CVs/current/"):
            if file.endswith(".pdf"):
                shutil.move(f"CVs/current/{file}", f"CVs/{file}")

        shutil.move("temp.pdf", f"CVs/current/{name}.pdf")

        # Clean up
        os.remove("temp.tex")
        os.remove("temp.log")
        os.remove("temp.aux")
        os.remove("temp.out")

        print("PDF generated successfully as CVs/current/temp.pdf")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_latex()
