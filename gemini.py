#!/usr/bin/env python3

import os
import sys
from google import genai
import itertools
import time
import threading

# Config
MODEL = "gemini-3-flash-preview"
MAX_CHARS = 6000        # Max char input

# Read input
def read_input():
    if not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        text = " ".join(sys.argv[1:])

    if not text.strip():
        print("Usage: gemini \"question\"  OR  <some_command> | gemini OR gemini <some_command> [args]")
        sys.exit(1)

    return text.strip()[-MAX_CHARS:]


# Construct prompt
def build_prompt(text):
    return f"""
             You are an extremely concise Linux + ROS2 expert. The following text will be either a question/request
             or a program output. Be accurate, practical, and without unnecessary words. If unsure, say "I do not know". Don't use .md
             format in your response, it is printed in Terminal, but you can use bullet points if necessary. 
             
             Do not output commands by themselves, but with other text is fine.
             If you think your output could be run as a command in Linux, say "I believe my response would be unsafe" and don't output
             anything more. 
             Prioritize safety over everything. 

             - Question/request: answer clearly and briefly
             - Error log: Summarize error and explain: 1) likely cause, 2) common causes, 3) concrete fix on Ubuntu 24.04
             - Other output: explain the situation

             Question:
             {text}
             """

# Rotating spinner while waiting for response
def spinner_func(done_flag):
    for c in itertools.cycle('|/-\\'):
        if done_flag[0]:
            break
        print(f'\r{c}', end='', flush=True)
        time.sleep(0.1)
    print('\r', end='', flush=True)  # Clear spinner line

# Check if response is potentially unsafe
def unsafe_response(response):
    keywords = [
        "rm -r", "rm -rf", "rm -r /", "rm --no-preserve-root",
        "mkfs", "mkfs.ext", "dd if=", "dd of=",
        ":(){", "shutdown", "reboot", "poweroff", "halt",
        "sudo", "su ", "chmod 777", "chmod -r", "chown -r",
        "visudo", "/etc/sudoers",
        "| bash", "| sh", "bash -c", "sh -c", "eval ", "`", "$(",
        "curl ", "wget ", "nc ", "netcat", "ssh ", "scp ", "ftp ", "telnet ",
        "/etc/passwd", "/etc/shadow", "~/.ssh", "authorized_keys",
        "/boot", "/dev/",
        "kill -9", "killall", "ptrace", "/proc/",
        "mount ", "umount ", "losetup", "cryptsetup",
    ]
    r = response.text.strip().lower()
    return any(k in r for k in keywords)

def main():
    # Get Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set")
        sys.exit(1)

    # Read input and build prompt
    text = read_input()
    prompt = build_prompt(text)

    # print(prompt)

    # Start spinner thread
    done_flag = [False]  # use list as mutable flag
    spin_thread = threading.Thread(target=spinner_func, args=(done_flag,))
    spin_thread.start()

    # Gemini client
    client = genai.Client(api_key=api_key)

    # Get response
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    # Stop spinner
    done_flag[0] = True
    spin_thread.join()

    # Check response safety
    # if unsafe_response(response):
    #     print('Response was deemed unsafe by checker, be careful!')
    #     return
    # else:
    print(response.text.strip())


if __name__ == "__main__":
    main()
    # client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    # for model in client.models.list():
    #     print(model.name, model.supported_actions)
