def execute(self, prompt: str, save_output: bool = True):
    """Execute interpreter command with prompt"""
    cmd = [
        "interpreter",
        "--local",
        "--model", self.model,
        "-y",  # Correct flag
        "-m", prompt
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if save_output:
        log_file = self.logs_dir / f"{self.agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, 'w') as f:
            json.dump({
                "agent": self.agent_type,
                "prompt": prompt,
                "output": result.stdout,
                "error": result.stderr,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    return result.stdout
