from flask import Flask, request, jsonify, render_template
import os
from craniofacial_cds.cds_system import CraniofacialCDS

# Initialize the CDS system with relative path
json_file_path = "full_text_Craniofacial_Surgery.json"
if not os.path.exists(json_file_path):
    raise FileNotFoundError(f"JSON file not found at: {json_file_path}")

cds = CraniofacialCDS(json_file_path)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    try:
        patient_data = request.json
        recommendations = cds.get_treatment_recommendations(patient_data)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/procedure_details', methods=['POST'])
def get_procedure_details():
    try:
        procedure_name = request.json.get('procedure_name')
        details = cds.get_procedure_details(procedure_name)
        return jsonify(details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/similar_cases', methods=['POST'])
def get_similar_cases():
    try:
        patient_data = request.json
        similar_cases = cds.get_similar_cases(patient_data)
        return jsonify(similar_cases)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Try different ports if 5001 is in use
    ports = [5001, 5002, 5003, 5004, 5005]
    for port in ports:
        try:
            print(f"Attempting to start server on port {port}...")
            app.run(debug=True, host='0.0.0.0', port=port)
            break
        except OSError as e:
            if port == ports[-1]:  # If this was the last port to try
                print(f"Could not start server on any port. Error: {e}")
                raise
            continue
