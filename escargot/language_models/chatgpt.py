# Copyright (c) 2023 ETH Zurich.
#                    All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# main author: Nils Blach

import backoff
import os
import random
import time
from typing import List, Dict, Union
from openai import OpenAI, OpenAIError
from openai.types.chat.chat_completion import ChatCompletion
import logging

from .abstract_language_model import AbstractLanguageModel


class ChatGPT:
    """
    The ChatGPT class handles interactions with the OpenAI models using the provided configuration.

    Inherits from the AbstractLanguageModel and implements its abstract methods.
    """

    def __init__(self, config):
        """
        Initialize the ChatGPT client.
        
        Args:
            config: Configuration dictionary containing API key and other settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up API key and organization
        self.api_key = config["api_key"]
        self.organization = config.get("organization", "")
        if not self.api_key:
            raise ValueError("API key is not set")
        if not self.organization:
            self.logger.warning("Organization is not set")
        
        # Initialize OpenAI client with base URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=config.get("api_base", "https://api.openai.com/v1")
        )
        
        # Set up model parameters
        self.model_id = config.get("model_id", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 2000)
        self.stop = config.get("stop", None)
        self.prompt_token_cost = config.get("prompt_token_cost", 0.001)
        self.response_token_cost = config.get("response_token_cost", 0.002)
        self.cache = config.get("cache", False)
        self.respone_cache = {}
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.cost = 0

    def query(
        self, query: str, num_responses: int = 1
    ) -> Union[List[ChatCompletion], ChatCompletion]:
        """
        Query the OpenAI model for responses.

        :param query: The query to be posed to the language model.
        :type query: str
        :param num_responses: Number of desired responses, default is 1.
        :type num_responses: int
        :return: Response(s) from the OpenAI model.
        :rtype: Dict
        """
        if self.cache and query in self.respone_cache:
            return self.respone_cache[query]

        if num_responses == 1:
            response = self.chat([{"role": "user", "content": query}], num_responses)
        else:
            response = []
            next_try = num_responses
            total_num_attempts = num_responses
            while num_responses > 0 and total_num_attempts > 0:
                try:
                    assert next_try > 0
                    res = self.chat([{"role": "user", "content": query}], next_try)
                    response.append(res)
                    num_responses -= next_try
                    next_try = min(num_responses, next_try)
                except Exception as e:
                    next_try = (next_try + 1) // 2
                    self.logger.warning(
                        f"Error in chatgpt: {e}, trying again with {next_try} samples"
                    )
                    time.sleep(random.randint(1, 3))
                    total_num_attempts -= 1

        if self.cache:
            self.respone_cache[query] = response
        return response

    @backoff.on_exception(backoff.expo, OpenAIError, max_tries=3)
    def ask(self, query):
        """
        Ask a question to the ChatGPT model.
        
        Args:
            query: The question to ask
            
        Returns:
            The model's response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": query}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=self.stop
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            raise

    @backoff.on_exception(backoff.expo, OpenAIError, max_time=10, max_tries=6)
    def chat(self, messages: List[Dict], num_responses: int = 1) -> ChatCompletion:
        """
        Send chat messages to the OpenAI model and retrieves the model's response.
        Implements backoff on OpenAI error.

        :param messages: A list of message dictionaries for the chat.
        :type messages: List[Dict]
        :param num_responses: Number of desired responses, default is 1.
        :type num_responses: int
        :return: The OpenAI model's response.
        :rtype: ChatCompletion
        """
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            n=num_responses,
            stop=self.stop,
        )

        self.prompt_tokens += response.usage.prompt_tokens
        self.completion_tokens += response.usage.completion_tokens
        prompt_tokens_k = float(self.prompt_tokens) / 1000.0
        completion_tokens_k = float(self.completion_tokens) / 1000.0
        self.cost = (
            self.prompt_token_cost * prompt_tokens_k
            + self.response_token_cost * completion_tokens_k
        )
        return response

    def get_response_texts(
        self, query_response: Union[List[ChatCompletion], ChatCompletion]
    ) -> List[str]:
        """
        Extract the response texts from the query response.

        :param query_response: The response dictionary (or list of dictionaries) from the OpenAI model.
        :type query_response: Union[List[ChatCompletion], ChatCompletion]
        :return: List of response strings.
        :rtype: List[str]
        """
        if not isinstance(query_response, List):
            query_response = [query_response]
        return [
            choice.message.content
            for response in query_response
            for choice in response.choices
        ]
