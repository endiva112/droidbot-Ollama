"""
DroidBot Input Policy 3: LLM-Guided Exploration using Ollama
This module implements AI-guided Android app exploration using local LLM via Ollama
"""

import logging
import random
import requests
import json
import re
import os
from .input_policy import UtgBasedInputPolicy
from .input_event import KeyEvent, IntentEvent, TouchEvent, ScrollEvent, SetTextEvent


class LLM_Guided_Policy(UtgBasedInputPolicy):
    """
    LLM-guided exploration policy using Ollama for decision making.
    
    This policy queries a local LLM (via Ollama) to decide which UI actions
    to take during app exploration. The LLM analyzes the current state and
    available actions to make intelligent exploration decisions.
    """
    
    def __init__(self, device, app, random_input, 
                 ollama_url=None,
                 ollama_model=None):
        super().__init__(device, app, random_input)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration from environment variables or defaults
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "gemma3:4b")
        
        self.logger.info(f"LLM_Guided_Policy initialized")
        self.logger.info(f"  Ollama URL: {self.ollama_url}")
        self.logger.info(f"  Ollama Model: {self.ollama_model}")
        
        # State tracking
        self.num_steps_outside = 0
        self.num_restarts = 0
        self.max_restarts = 5
        self.max_steps_outside = 5
        self.max_steps_outside_kill = 10
        
        # Statistics for monitoring
        self.successful_queries = 0
        self.failed_queries = 0
        self.fallback_to_random = 0
        
    def generate_event_based_on_utg(self):
        """
        Generate an event by consulting the LLM about the current state.
        
        The workflow is:
        1. Check app state (foreground/background)
        2. Get possible UI events
        3. Build prompt describing the state and options
        4. Query Ollama for decision
        5. Execute selected action (or fallback to random)
        """
        current_state = self.current_state
        self.logger.debug(f"Current state: {current_state.state_str}")
        
        # Handle app not in foreground
        app_depth = current_state.get_app_activity_depth(self.app)
        
        if app_depth < 0:
            # App not in activity stack - start it
            self.logger.info("App not in activity stack, starting...")
            self.num_restarts += 1
            
            if self.num_restarts > self.max_restarts:
                self.logger.warning(f"App restarted {self.num_restarts} times, may be unstable")
            
            return IntentEvent(intent=self.app.get_start_intent())
        
        elif app_depth > 0:
            # App in background
            self.num_steps_outside += 1
            
            if self.num_steps_outside > self.max_steps_outside:
                self.logger.info(f"App in background for {self.num_steps_outside} steps, going back...")
                
                if self.num_steps_outside > self.max_steps_outside_kill:
                    # Force restart
                    self.num_steps_outside = 0
                    return IntentEvent(intent=self.app.get_stop_intent())
                
                return KeyEvent(name="BACK")
        else:
            # App in foreground - reset counter
            self.num_steps_outside = 0
            self.num_restarts = 0
        
        # Get possible events from current state
        possible_events = current_state.get_possible_input()
        
        # Always add BACK as an option
        possible_events.append(KeyEvent(name="BACK"))
        
        if not possible_events:
            self.logger.warning("No possible events found, pressing BACK")
            return KeyEvent(name="BACK")
        
        # Build prompt for LLM
        prompt = self._build_exploration_prompt(current_state, possible_events)
        
        # Query Ollama for action selection
        try:
            selected_idx = self._query_ollama(prompt, len(possible_events))
            selected_event = possible_events[selected_idx]
            
            self.successful_queries += 1
            self.logger.info(
                f"LLM selected action {selected_idx}/{len(possible_events)}: "
                f"{type(selected_event).__name__}"
            )
            
            return selected_event
            
        except Exception as e:
            self.failed_queries += 1
            self.fallback_to_random += 1
            
            self.logger.warning(f"LLM query failed: {e}")
            self.logger.info("Falling back to random action")
            
            if self.logger.level <= logging.DEBUG:
                import traceback
                traceback.print_exc()
            
            return random.choice(possible_events)
    
    def _build_exploration_prompt(self, state, events):
        """
        Build a prompt for the LLM describing the current state and available actions.
        
        The prompt is designed to get a numeric response indicating which action to take.
        """
        # Get activity name (clean format)
        activity = state.foreground_activity
        if '/' in activity:
            activity = activity.split('/')[-1]
        
        # Build action descriptions
        action_descriptions = []
        for i, event in enumerate(events):
            desc = self._describe_event_for_prompt(event, i)
            action_descriptions.append(desc)
        
        # Construct prompt
        prompt = f"""You are an AI agent testing an Android application. Your goal is to thoroughly explore the app's functionality by selecting the most promising UI actions.

Current Activity: {activity}

Available Actions:
{chr(10).join(action_descriptions)}

Guidelines for selection:
- Prioritize interactive elements (buttons, inputs) over navigation
- Prefer unexplored UI elements when possible
- Avoid excessive BACK actions that might exit the app
- Try to progress through the app's features systematically

Respond with ONLY the number of the action to take (0-{len(events)-1}).
Do not include any explanation or other text.

Selected action number:"""
        
        return prompt
    
    def _describe_event_for_prompt(self, event, index):
        """
        Generate a human-readable description of an event for the LLM prompt.
        """
        if isinstance(event, TouchEvent) and event.view:
            view = event.view
            text = view.get('text', '') or ''  # Manejar None
            text = text.strip() if text else ''
            
            content_desc = view.get('content_description', '') or ''
            content_desc = content_desc.strip() if content_desc else ''
            
            resource_id = view.get('resource_id', '') or ''
            view_class = view.get('class', '') or ''
            view_class = view_class.split('.')[-1] if view_class else 'Unknown'
            
            # Build description from available info
            parts = []
            
            if text and len(text) > 0:
                # Truncate long text
                display_text = text[:30] + '...' if len(text) > 30 else text
                parts.append(f"'{display_text}'")
            
            if content_desc and content_desc != text:
                display_desc = content_desc[:30] + '...' if len(content_desc) > 30 else content_desc
                parts.append(f"({display_desc})")
            
            if not parts and resource_id:
                # Use resource ID if no text
                rid_clean = resource_id.split('/')[-1] if '/' in resource_id else resource_id
                parts.append(f"[{rid_clean}]")
            
            if not parts:
                # Fallback to class name
                parts.append(f"<{view_class}>")
            
            description = ' '.join(parts)
            return f"{index}. Touch {description}"
        
        elif isinstance(event, ScrollEvent):
            direction = event.direction.upper() if hasattr(event, 'direction') else 'DOWN'
            view_desc = ""
            if event.view and event.view.get('class'):
                view_class = event.view['class'].split('.')[-1]
                view_desc = f" in {view_class}"
            return f"{index}. Scroll {direction}{view_desc}"
        
        elif isinstance(event, SetTextEvent):
            view_hint = "input field"
            if event.view:
                text = event.view.get('text', '') or ''
                if text:
                    view_hint = f"'{text}'"
            return f"{index}. Enter text in {view_hint}"
        
        elif isinstance(event, KeyEvent):
            key_name = event.name if hasattr(event, 'name') else 'KEY'
            return f"{index}. Press {key_name}"
        
        else:
            # Generic fallback
            event_type = type(event).__name__
            return f"{index}. {event_type}"


    def _query_ollama(self, prompt, max_index):
        """
        Query Ollama API and extract action index from response.
        
        Args:
            prompt: The prompt to send to Ollama
            max_index: Maximum valid index (exclusive)
            
        Returns:
            int: Index of selected action (0 to max_index-1)
            
        Raises:
            Exception: If query fails or response is invalid
        """
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        self.logger.debug(f"Querying Ollama at {self.ollama_url}")
        
        try:
            response = requests.post(
                self.ollama_url, 
                json=payload, 
                timeout=30
            )
            response.raise_for_status()
            
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Could not connect to Ollama at {self.ollama_url}. "
                "Make sure Ollama is running (ollama serve)"
            )
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out after 30 seconds")
        
        # Parse response
        result = response.json()
        answer = result["message"]["content"].strip()
        
        self.logger.debug(f"Ollama raw response: '{answer}'")
        
        # Extract action index
        selected = self._extract_action_index(answer, max_index)
        
        return selected
    
    def _extract_action_index(self, text, max_index):
        """
        Extract a valid action index from LLM response text.
        
        Tries multiple strategies:
        1. Parse text directly as integer
        2. Extract first number from text
        3. Fallback to random if no valid number found
        """
        text = text.strip()
        
        # Strategy 1: Direct parse
        try:
            selected = int(text)
            if 0 <= selected < max_index:
                return selected
        except ValueError:
            pass
        
        # Strategy 2: Extract numbers from text
        numbers = re.findall(r'\d+', text)
        for num_str in numbers:
            try:
                selected = int(num_str)
                if 0 <= selected < max_index:
                    return selected
            except ValueError:
                continue
        
        # Strategy 3: Fallback to random
        self.logger.warning(
            f"Could not extract valid index from '{text}', "
            f"using random selection"
        )
        return random.randint(0, max_index - 1)
    
    def stop(self):
        """
        Called when exploration stops. Log statistics.
        """
        total_queries = self.successful_queries + self.failed_queries
        
        if total_queries > 0:
            success_rate = (self.successful_queries / total_queries) * 100
            self.logger.info("=== LLM Policy Statistics ===")
            self.logger.info(f"Total queries: {total_queries}")
            self.logger.info(f"Successful: {self.successful_queries} ({success_rate:.1f}%)")
            self.logger.info(f"Failed: {self.failed_queries}")
            self.logger.info(f"Random fallbacks: {self.fallback_to_random}")