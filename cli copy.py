import os
from craniofacial_cds.cds_system import CraniofacialCDS

def main():
    # Set the API key
    os.environ["OPENAI_API_KEY"] = ""
    
    # Initialize the CDS system
    json_file_path = "full_text_Craniofacial_Surgery.json"
    cds = CraniofacialCDS(json_file_path)
    
    while True:
        print("\nCraniofacial Clinical Decision Support System")
        print("1. Get Treatment Recommendations")
        print("2. Get Procedure Details")
        print("3. Find Similar Cases")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            # Get treatment recommendations
            patient_data = {
                "age": int(input("Enter patient age: ")),
                "gender": input("Enter patient gender: "),
                "medical_history": input("Enter medical history: "),
                "current_condition": input("Enter current condition: ")
            }
            recommendations = cds.get_treatment_recommendations(patient_data)
            print("\nRecommendations:")
            print(recommendations)
            
        elif choice == "2":
            # Get procedure details
            procedure_name = input("Enter procedure name: ")
            details = cds.get_procedure_details(procedure_name)
            print("\nProcedure Details:")
            print(details)
            
        elif choice == "3":
            # Find similar cases
            patient_data = {
                "age": int(input("Enter patient age: ")),
                "gender": input("Enter patient gender: "),
                "medical_history": input("Enter medical history: "),
                "current_condition": input("Enter current condition: ")
            }
            similar_cases = cds.get_similar_cases(patient_data)
            print("\nSimilar Cases:")
            print(similar_cases)
            
        elif choice == "4":
            print("Thank you for using the CDS system!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
