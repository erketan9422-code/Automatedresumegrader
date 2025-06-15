import os
import spacy
from flask import Flask, request, jsonify, render_template_string, send_file
from weasyprint import HTML

app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Route to serve the index.html file
@app.route('/')
def index():
    return render_template_string(open("static/index.html").read())

# Function to process text with spaCy
def process_text_with_spacy(text):
    doc = nlp(text)
    
    # Example: Extract named entities (e.g., company names, job titles, etc.)
    entities = [ent.text for ent in doc.ents]
    
    # Example: You can also extract skills (for now, let's use the most frequent nouns as skills)
    skills = [token.text for token in doc if token.pos_ == "NOUN"]
    
    return entities, skills

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    try:
        data = request.json
        # Extract form data
        name = data.get("name", "")
        email = data.get("email", "")
        phone = data.get("phone", "")
        linkedin = data.get("linkedin", "")
        address = data.get("address", "")
        skills = data.get("skills", [])
        education = data.get("education", "")
        experience = data.get("experience", "")
        projects = data.get("projects", "")

        # Process the experience and education fields with spaCy
        experience_entities, experience_skills = process_text_with_spacy(experience)
        education_entities, education_skills = process_text_with_spacy(education)

        # Generate HTML content for the resume
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{  font-family: 'Times New Roman', Times, serif; margin: 20px;  color: black; font-size:14px }}
                    h1, h2 {{  color: black;  }}
                    .resume-header {{ text-align: center; }}
                    .section {{ margin-bottom: 20px; }}
                    .skills-list {{ list-style-type: none; padding: 0; }}
                    .skills-list li {{ display: inline-block; margin-right: 10px; }}
                </style>
            </head>
            <body>
                <div class="resume-header">
                    <h1>{name}</h1>
                    <p>{email} | {phone} | <a href="{linkedin}">{linkedin}</a></p>
                    <p>{address}</p>
                </div>

                <div class="section">
                    <h2>Education</h2>
                    <p>{education}</p>
                    <h3>Entities Detected in Education:</h3>
                    <ul>
                        {''.join([f'<li>{entity}</li>' for entity in education_entities])}
                    </ul>
                </div>

                <div class="section">
                    <h2>Skills</h2>
                    <ul class="skills-list">
                        {''.join([f'<li>{skill}</li>' for skill in skills])}
                    </ul>
                    <h3>Skills Detected from Experience:</h3>
                    <ul class="skills-list">
                        {''.join([f'<li>{skill}</li>' for skill in experience_skills])}
                    </ul>
                </div>

                <div class="section">
                    <h2>Experience</h2>
                    <p>{experience}</p>
                    <h3>Entities Detected in Experience:</h3>
                    <ul>
                        {''.join([f'<li>{entity}</li>' for entity in experience_entities])}
                    </ul>
                </div>

                <div class="section">
                    <h2>Projects & Achievements</h2>
                    <p>{projects}</p>
                </div>
            </body>
        </html>
        """

        # Generate the PDF using weasyprint
        html = HTML(string=html_content)
        pdf_file_path = "resume.pdf"
        html.write_pdf(pdf_file_path)

        # Check if the PDF was generated successfully
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError("Failed to generate PDF.")

        # Send the generated PDF to the user
        return send_file(pdf_file_path, as_attachment=True, mimetype='application/pdf')

    except Exception as e:
        print(f"Error generating resume: {e}")
        return jsonify({"error": f"Error generating resume: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
