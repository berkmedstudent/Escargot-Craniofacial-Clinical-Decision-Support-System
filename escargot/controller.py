class SimpleController:
    def __init__(self):
        self.history = []
    
    def process(self, query, language_model):
        try:
            response = language_model.ask(query)
            self.history.append({"query": query, "response": response})
            return response
        except Exception as e:
            print(f"Error processing query: {e}")
            return None
    
    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history.clear() 