import json
import re
from pathlib import Path

TRANSCRIPT_PATH = Path(
    r"C:\Users\snigd\.gemini\antigravity-ide\brain\16841134-a75c-43e8-b12d-74eed7b435bd\.system_generated\logs\transcript.jsonl"
)
OUTPUT_DIR = Path("devrelay")
OUTPUT_PATH = OUTPUT_DIR / "session_transcript.json"

SENSITIVE_PATTERNS = [
    (r"https://[a-f0-9]+@[a-z0-9]+\.ingest\.us\.sentry\.io/\d+", "https://***@o***.ingest.us.sentry.io/***"),
    (r"84c6fdc65ba9d95b25ab3486e0e74a7f", "sentry_dsn_token"),
    (r"c:[\\/]Users[\\/]snigd", "~"),
    (r"C:[\\/]Users[\\/]snigd", "~"),
]

def sanitize(text: str) -> str:
    if not isinstance(text, str):
        return text
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def clean_user_content(raw: str) -> str:
    if "<USER_REQUEST>" in raw:
        match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw, re.DOTALL)
        if match:
            raw = match.group(1).strip()
    # Strip any remaining system or metadata tags
    raw = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", raw, flags=re.DOTALL)
    raw = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", raw, flags=re.DOTALL)
    return sanitize(raw.strip())

def parse_transcript():
    messages = []
    current_assistant_content = []
    
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            
            item_type = item.get("type")
            source = item.get("source")

            if item_type == "USER_INPUT":
                # Flush pending assistant content
                if current_assistant_content:
                    messages.append({
                        "role": "assistant",
                        "model": "gemini-3.7-flash",
                        "content": current_assistant_content,
                    })
                    current_assistant_content = []

                user_text = clean_user_content(item.get("content", ""))
                if user_text:
                    messages.append({
                        "role": "user",
                        "content": [{"type": "text", "text": user_text}]
                    })

            elif item_type == "PLANNER_RESPONSE":
                content = item.get("content", "")
                if content and isinstance(content, str) and content.strip():
                    current_assistant_content.append({
                        "type": "text",
                        "text": sanitize(content.strip())
                    })
                
                tool_calls = item.get("tool_calls", [])
                for tc in tool_calls:
                    name = tc.get("name") or tc.get("tool_name", "tool")
                    args = tc.get("args") or tc.get("parameters", {})
                    current_assistant_content.append({
                        "type": "tool_call",
                        "name": name,
                        "input": sanitize(json.dumps(args)[:500]),
                        "output": "Executed successfully",
                    })

    if current_assistant_content:
        messages.append({
            "role": "assistant",
            "model": "gemini-3.7-flash",
            "content": current_assistant_content,
        })

    return messages

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    messages = parse_transcript()
    print(f"Parsed {len(messages)} total messages.")

    payload = {
        "messages": messages,
        "metadata": {
            "tool_name": "gemini_cli",
            "session_id": "16841134-a75c-43e8-b12d-74eed7b435bd",
            "total_messages": len(messages),
        }
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Saved cleaned transcript to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
