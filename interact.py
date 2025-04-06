import os
from craniofacial_cds.cds_system import CraniofacialCDS

def initialize_cds():
    # Set the API key
    os.environ["OPENAI_API_KEY"] = "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"
    
    # Initialize the CDS system
    json_file_path = "full_text_Craniofacial_Surgery.json"
    print(f"Initializing CDS system with file: {json_file_path}")
    
    try:
        cds = CraniofacialCDS(json_file_path)
        print("CDS system initialized successfully!")
        return cds
    except Exception as e:
        print(f"Error initializing CDS system: {e}")
        return None

def example_interaction(cds):
    # Example: Get treatment recommendations
    print("\nGetting treatment recommendations for a sample patient...")
    patient_data = {
        "age": 25,
        "gender": "female",
        "medical_history": "No significant medical history",
        "current_condition": "Cleft palate"
    }
    
    try:
        recommendations = cds.get_treatment_recommendations(patient_data)
        print("\nRecommendations:")
        print(recommendations)
    except Exception as e:
        print(f"Error getting recommendations: {e}")

if __name__ == "__main__":
    print("Starting Craniofacial CDS System...")
    cds = initialize_cds()
    
    if cds:
        example_interaction(cds)
    else:
        print("Failed to initialize CDS system.") 