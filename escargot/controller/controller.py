# Copyright (c) 2023 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# main author: Nils Blach

import json
import logging
from typing import List, Optional, Dict, Any
from escargot.language_models import AbstractLanguageModel
from escargot.operations import GraphOfOperations, Thought
from escargot.prompter import ESCARGOTPrompter
from escargot.parser import ESCARGOTParser
from escargot.coder import Coder
import copy
import dill as pickle
import os

class Controller:
    """
    Controller class to manage the execution flow of the Graph of Operations,
    generating the Graph Reasoning State.
    This involves language models, graph operations, prompting, and parsing.
    """

    def __init__(
        self,
        lm: AbstractLanguageModel,
        graph: GraphOfOperations,
        prompter: ESCARGOTPrompter,
        parser: ESCARGOTParser,
        logger: logging.Logger,
        coder: Coder,
        problem_parameters: Dict[str, Any],
    ) -> None:
        """
        Initialize the Controller instance with the language model,
        operations graph, prompter, parser, and problem parameters.
        """
        self.logger = logger
        self.lm = lm
        self.graph = graph
        self.prompter = prompter
        self.parser = parser
        self.original_problem_parameters = problem_parameters
        self.problem_parameters = problem_parameters
        self.run_executed = False
        self.got_steps = {}
        self.final_thought = None
        self.execution_queue = []
        self.max_run_tries = 3
        self.max_operation_tries = 2
        self.coder = coder

    def initialize_execution_queue(self) -> None:
        """
        Initialize the execution queue with the root operations of the graph.
        """
        self.execution_queue = [
            operation for operation in self.graph.operations if operation.can_be_executed()
        ]
    
    def get_execution_queue(self) -> List[str]:
        """
        Get the execution queue.

        :return: The execution queue.
        """
        return [operation.get_thoughts()[0].predecessors[0].state["previous_phase"] for operation in self.execution_queue]
    
    def get_current_operation(self) -> Optional[str]:
        """
        Get the current operation being executed.

        :return: The name of the current operation, or None if no operation is being executed.
        """
        if not self.execution_queue:
            return None
        return self.execution_queue[0].predecessors[0].get_thoughts()[0].state["previous_phase"]
    
    def get_next_operation(self) -> Optional[str]:
        """
        Get the next operation to be executed.

        :return: The name of the next operation, or None if no operation is left to execute.
        """
        if not self.execution_queue:
            return None
        return self.execution_queue[0].predecessors[0].get_thoughts()[0].state["phase"]

    def execute_step(self) -> Optional[Thought]:
        """
        Execute one step from the execution queue.

        :return: The thought generated by the executed operation, or None if no operation is left to execute.
        """
        if not self.execution_queue:
            self.initialize_execution_queue()

        if not self.execution_queue:
            self.logger.debug("No more operations to execute.")
            return None

        current_operation = self.execution_queue.pop(0)
        current_operation_backup = copy.copy(current_operation)
        
        tries = 0
        while tries < self.max_operation_tries:
            try:
                current_operation.execute(
                    self.lm, self.prompter, self.parser, self.got_steps, self.logger, self.coder, **self.problem_parameters
                )
                break
            except Exception as e:
                self.logger.error("Error executing operation %s: %s", current_operation.operation_type, e)
                current_operation = copy.copy(current_operation_backup)
                tries += 1

        del current_operation_backup

        if tries == self.max_operation_tries:
            self.logger.error("Max tries reached on executing operation %s", current_operation.operation_type)
            return None
        
        for operation in current_operation.successors:
            if operation.can_be_executed():
                self.execution_queue.append(operation)
        
        self.final_thought = current_operation.get_thoughts()[0]
        
        return self.final_thought

    def run(self) -> None:
        """
        Run the controller and execute the operations from the Graph of Operations based on their readiness.
        Ensures the program is in a valid state before execution.
        """
        assert self.graph.roots is not None, "The operations graph has no root"
        
        while not self.run_executed and self.max_run_tries > 0:
            self.max_run_tries -= 1
            self.execution_queue = []
            self.got_steps = {}
            self.problem_parameters = copy.copy(self.original_problem_parameters)
            self.initialize_execution_queue()
            
            while self.execution_queue:
                self.execute_step()

            if self.final_thought.state["phase"] == "output":
                self.logger.info("All operations executed")
                self.run_executed = True

        if self.max_run_tries == 0:
            self.logger.error("Max tries reached on executing controller")


    def get_final_thoughts(self) -> List[List[Thought]]:
        """
        Retrieve the final thoughts after all operations have been executed.

        :return: List of thoughts for each operation in the graph's leaves.
        """
        assert self.run_executed, "The run method has not been executed"
        return [operation.get_thoughts() for operation in self.graph.leaves]

    def serialize_operation(self, operation) -> Dict[str, Any]:
        """
        Serialize an operation to a dictionary.

        :param operation: The operation to serialize.
        :return: The serialized operation.
        """
        operation_serialized = {
            "operation": operation.operation_type.name,
            "thoughts": [thought.state for thought in operation.get_thoughts()],
        }
        return operation_serialized

    def output_graph(self, path: str) -> None:
        """
        Serialize the state and results of the operations graph to a JSON file.

        :param path: The path to the output file.
        """
        output = [self.serialize_operation(op) for op in self.graph.operations]

        output.append(
            {
                "prompt_tokens": self.lm.prompt_tokens,
                "completion_tokens": self.lm.completion_tokens,
                "cost": self.lm.cost,
            }
        )

        with open(path, "w") as file:
            json.dump(output, file, indent=2)

    def save_controller_state(self, path: str) -> None:
        if path == "":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, "controller_state.pkl")

        logger = self.logger
        lm = self.lm
        prompter = self.prompter
        parser = self.parser
        coder = self.coder

        self.logger = None
        self.lm = None
        self.prompter = None
        self.parser = None
        self.coder = None

        with open(path, "wb") as file:
            pickle.dump(self, file)

        self.logger = logger
        self.lm = lm
        self.prompter = prompter
        self.parser = parser
        self.coder = coder
        self.logger.info("Controller state saved to %s", path)

    @staticmethod
    def load_state(file_path: str, logger, lm, prompter, parser, coder):
        """
        Load the state of the controller from a file.

        :param file_path: The path to the file from which the state will be loaded.
        :param logger: The logger to be restored.
        :param lm: The language model to be restored.
        :param prompter: The prompter to be restored.
        :param parser: The parser to be restored.
        :param coder: The coder to be restored.
        :return: The controller instance with the loaded state.
        """
        with open(file_path, 'rb') as file:
            controller = pickle.load(file)

        # Restore non-pickleable objects
        controller.logger = logger
        controller.lm = lm
        controller.prompter = prompter
        controller.parser = parser
        controller.coder = coder

        controller.logger.info("Controller state loaded from %s", file_path)
        return controller

    def go_to_phase(self, phase: str) -> None:
        """
        Go to a specific phase in the graph of operations.

        :param phase: The phase to go to.
        """
        # Find the operation corresponding to the given phase
        for operation in self.graph.operations:
            if operation.get_thoughts()[0].state["phase"] == phase:
                self.execution_queue = [operation]
                self.logger.info("Moved to phase %s", phase)
                return
        
        self.logger.error("Phase %s not found in the graph of operations", phase)