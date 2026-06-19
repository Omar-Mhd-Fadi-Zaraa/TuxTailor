import json
import sys

def create_message_list(messages):
    return messages


if __name__ == "__main__":
    messages = json.load(sys.stdin)
    result = create_message_list(messages)
    sys.stdout.write(json.dumps(result))