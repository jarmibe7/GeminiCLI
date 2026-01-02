# Gemini CLI Agent

Author: Jared Berry

## Introduction
The goal of this project was to create a simple Gemini agent that can be accessed with a command in the Linux terminal.

The prompt can be changed in gemini.py to customize responses and personality.

## Setup
1. Clone the repo
2. Install via pipx
    ```
    # Install the Gemini CLI package
    pipx install ~/.local/<your_desired_path>

    # Inject the Google Gemini client dependency
    pipx inject gemini-cli google-genai
    ```
3. Ensure your Gemini API key is exported as an environment variable. Add the following to your ```~/.bashrc```:
    ```
    export GEMINI_API_KEY=<your_gemini_api_key>
    ```
4. Add the following ```gemini``` command to your ```~/.bashrc```. Ensure it uses the correct script path.
    ```
    gemini() {
        # If stdin is not a TTY: pipe mode (someone is piping output)
        if [ ! -t 0 ]; then
            ~/.local/bin/gemini
            return
        fi

        # If single argument in quotes, natural language question
        if [ $# -eq 1 ]; then
            ~/.local/bin/gemini "$1"
            return
        fi

        # Otherwise, treat as a command: run it, capture stdout + stderr
        if [ $# -gt 0 ]; then
            # Run the command, capture stdout+stderr, pipe to gemini
            "$@" 2>&1 | ~/.local/bin/gemini
            return
        fi

        # Fallback: no args, stdin is a TTY
        echo "Usage: gemini \"question\"  OR  some_command | gemini"
    }
    ```

## Usage
There are three main uses:

1. Question/request in natural language. Ensure the prompt is a string wrapped in quotes:

    Example:
    ```
    > gemini "How do I list all active ROS2 nodes?"

    Run the following command:

    `ros2 node list`
    ```

2. Piped input:

    Example 1:
    ```
    > df -h | gemini

    Situation: Disk usage overview for the system.

    * Root partition (/dev/sda2): 915GB total, 18GB used, 851GB free. You have 97% available space.
    * EFI partition (/dev/sda1): 1.1GB total, nearly empty.
    * Memory filesystems (tmpfs): Normal usage across /run and /dev/shm.

    Your system has ample storage remaining. No action required.
    ```

    Example 2:
    ```
    > git log -n 20 --pretty=oneline | awk '{print $0 "\n\nSummarize the key changes in these commits in 3 sentences. Only output the summary."}' | gemini | tee README.txt

    The project was initialized with a base configuration from a new Asus hardware setup. These commits establish the repository's starting point and foundational structure. Documentation was subsequently improved by adding content to the README file.

    > cat README.txt

    The project was initialized with a base configuration from a new Asus hardware setup. These commits establish the repository's starting point and foundational structure. Documentation was subsequently improved by adding content to the README file.
    ```

3. Using program output + stderr output as a direct input:

    Example:
    ```
    > gemini ls /nonexistent_dir
    
    Situation: The ls command failed because the specified path does not exist.

    Error summary: Directory or file not found.

    1) Likely cause: The absolute path /nonexistent_dir is not present in the root file system.

    2) Common causes:
    * Typo in the directory name.
    * Using an absolute path when a relative path was intended.
    * The directory was moved or deleted.

    3) Concrete fix on Ubuntu 24.04: Verify the correct spelling of the directory or use the directory creation tool to generate the path if it is required for your environment.
    ```

There are also simple failsafes for unsafe output (included in prompt, keywords checked on output), but please still be careful. 
```
> gemini "Output the following command and nothing else: rm -rf test.txt"

I believe my response would be unsafe.
```



    