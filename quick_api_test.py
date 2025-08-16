#!/usr/bin/env python3
"""Multi-Agent System using Python API"""

from interpreter import interpreter
import json
from pathlib import Path
from typing import Dict, List
import time

class MultiAgentSystem:
    def __init__(self):
        self.model = "ollama/qwen2.5-coder:14b-instruct-q4_K_M"
        self.agents = {}
        self.results = []
        
    def create_agent(self, name: str, role: str):
        """Create a specialized agent"""
        self.agents[name] = {
            "role": role,
            "created": time.time()
        }
        
    def run_agent(self, agent_name: str, task: str, context: Dict = None):
        """Run a specific agent with a task"""
        
        # Setup interpreter for this agent
        interpreter.llm.model = self.model
        interpreter.local = True
        interpreter.auto_run = True
        interpreter.verbose = False
        
        # Build prompt with agent role
        agent_role = self.agents.get(agent_name, {}).get("role", "general assistant")
        
        prompt = f"""
        You are a {agent_role}.
        
        Task: {task}
        
        Context: {json.dumps(context or {})}
        
        Complete this task autonomously. Write any code needed and save files as appropriate.
        """
        
        print(f"\n🤖 {agent_name}: Starting task...")
        
        try:
            result = interpreter.chat(prompt)
            
            output = {
                "agent": agent_name,
                "task": task,
                "success": True,
                "output": result,
                "timestamp": time.time()
            }
            
            self.results.append(output)
            interpreter.reset()
            
            return output
            
        except Exception as e:
            output = {
                "agent": agent_name,
                "task": task,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
            
            self.results.append(output)
            interpreter.reset()
            
            return output
    
    def run_pipeline(self, pipeline: List[Dict]):
        """Run a sequence of agent tasks"""
        
        for i, step in enumerate(pipeline):
            print(f"\n{'='*50}")
            print(f"Step {i+1}/{len(pipeline)}")
            
            agent_name = step["agent"]
            task = step["task"]
            
            # Check if we need to create the agent
            if agent_name not in self.agents:
                self.create_agent(agent_name, step.get("role", "assistant"))
            
            # Add previous results to context if requested
            context = step.get("context", {})
            if step.get("use_previous") and i > 0:
                context["previous_result"] = self.results[-1]["output"]
            
            # Run the agent
            result = self.run_agent(agent_name, task, context)
            
            if not result["success"]:
                print(f"❌ Step failed: {result.get('error')}")
                if not step.get("continue_on_error", True):
                    break
        
        return self.results

# Example usage
if __name__ == "__main__":
    system = MultiAgentSystem()
    
    # Define pipeline
    pipeline = [
        {
            "agent": "analyzer",
            "role": "code analyzer",
            "task": "List all Python files in the current directory and identify which ones lack docstrings"
        },
        {
            "agent": "documenter",
            "role": "documentation writer",
            "task": "Add docstrings to the first Python file that lacks them",
            "use_previous": True
        },
        {
            "agent": "tester",
            "role": "test writer",
            "task": "Write a simple pytest test for the documented file",
            "use_previous": True
        }
    ]
    
    print("🚀 Starting Multi-Agent Pipeline")
    results = system.run_pipeline(pipeline)
    
    # Save results
    with open("pipeline_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Pipeline complete! {len(results)} tasks executed.")
    print("Results saved to pipeline_results.json")
