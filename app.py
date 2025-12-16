import os
import pdfplumber
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from optimizer import calculate_plan, STEM_CATEGORIES # Import our fixed logic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    schedule = None
    if request.method == 'POST':
        if 'file' not in request.files: return "No file"
        file = request.files['file']
        if file.filename == '': return "No selected file"
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract Text
            full_text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text: full_text += text + "\n"
            
            # Run the Optimizer
            schedule = calculate_plan(full_text)
            
    return render_template('index.html', schedule=schedule, stem_categories=STEM_CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)