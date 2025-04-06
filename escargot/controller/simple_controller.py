class SimpleController:
    def __init__(self):
        self.history = []
    
    def process(self, query, language_model):
        """
        Process a query using the language model.
        
        Args:
            query: The query to process
            language_model: The language model to use
            
        Returns:
            The model's response
        """
        try:
            # Get response from language model
            response = language_model.ask(query)
            
            # Store in history
            self.history.append({
                "query": query,
                "response": response
            })
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return None
    
    def get_history(self):
        """Get the query history."""
        return self.history
    
    def clear_history(self):
        """Clear the query history."""
        self.history.clear() 