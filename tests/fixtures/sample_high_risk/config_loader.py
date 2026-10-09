"""Configuration loader.

Demo purpose: intentionally high-risk. Contains hardcoded credentials,
an unclosed file handle, and dynamic code execution via eval/exec.
"""

API_KEY = "sk_live_51Hf9aBcDeFgHiJkLmNoPqRsT"  # hardcoded credential (flagged)
SECRET_TOKEN = "super-secret-token-please-change"  # hardcoded credential (flagged)


def load_config(path):
    f = open(path)  # unclosed resource (flagged)
    contents = f.read()
    return contents


def apply_dynamic_setting(expression):
    return eval(expression)  # dynamic code injection risk (flagged)


def run_custom_hook(code_string):
    exec(code_string)  # dynamic code injection risk (flagged)
