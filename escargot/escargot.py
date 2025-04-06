import os
import logging
import io
from .language_models import ChatGPT
from .memory import SimpleMemory
from .controller import SimpleController

class Escargot:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.language_model = None
        self.memory = None
        self.controller = None
        
        # Initialize language model
        if 'language_model' in config:
            self.language_model = ChatGPT(config['language_model'])
        
        # Initialize memory and controller in simple mode
        self.memory = SimpleMemory()
        self.controller = SimpleController()
        
    def ask(self, query, debug_level=0):
        """
        Ask a question to the language model.
        
        Args:
            query: The question to ask
            debug_level: Level of debug information to print (0-3)
            
        Returns:
            The model's response
        """
        try:
            # Set up logging
            log_stream, c_handler, f_handler = self.setup_logger(debug_level)
            
            # Process query through controller
            response = self.controller.process(query, self.language_model)
            
            # Clean up logging
            if debug_level > 0:
                self.cleanup_logger(log_stream, c_handler, f_handler)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error executing controller: {str(e)}")
            raise e
    
    def setup_logger(self, debug_level):
        """Set up logging with the specified debug level."""
        log_stream = io.StringIO()
        f_handler = logging.StreamHandler(log_stream)
        c_handler = logging.StreamHandler()
        
        if debug_level == 0:
            self.logger.setLevel(logging.ERROR)
            c_handler.setLevel(logging.ERROR)
            f_handler.setLevel(logging.ERROR)
        elif debug_level == 1:
            self.logger.setLevel(logging.WARNING)
            c_handler.setLevel(logging.WARNING)
            f_handler.setLevel(logging.WARNING)
        elif debug_level == 2:
            self.logger.setLevel(logging.INFO)
            c_handler.setLevel(logging.INFO)
            f_handler.setLevel(logging.INFO)
        elif debug_level == 3:
            self.logger.setLevel(logging.DEBUG)
            c_handler.setLevel(logging.DEBUG)
            f_handler.setLevel(logging.DEBUG)
            
        c_format = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s(%(lineno)d) - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(c_format)
        self.logger.addHandler(f_handler)
        self.logger.addHandler(c_handler)
        
        return log_stream, c_handler, f_handler
    
    def cleanup_logger(self, log_stream, c_handler, f_handler):
        """Clean up logging handlers."""
        self.logger.removeHandler(c_handler)
        c_handler.close()
        self.logger.removeHandler(f_handler)
        f_handler.close() 