# 🧪 HOW TO TEST LLM ON TERMINAL

## Quick Terminal Testing Guide

---

## ✅ Option 1: One-Liner Test (Fastest)

```bash
cd /Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen

python3 -c "
import os
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter
llm = LLMAdapter()
response = llm.generate('What is AI?', max_tokens=200)
print('Answer:', response['text'])
"
```

**Result**: You'll get the LLM response instantly!

---

## ✅ Option 2: Interactive Python Shell (Best for Learning)

```bash
cd /Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen

python3
```

Then type these commands one by one:

```python
# Step 1: Load environment
import os
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

# Step 2: Import LLM adapter
from agents.llm_adapter import LLMAdapter

# Step 3: Initialize
llm = LLMAdapter()

# Step 4: Check status
print(f"Provider: {llm.provider}")
print(f"Model: {llm.model}")
print(f"Available: {llm.is_available}")

# Step 5: Ask a question
response = llm.generate("What is machine learning?", max_tokens=256)

# Step 6: Print response
print("Full response:")
print(response['text'])

# Step 7: Check metadata
print("\nMetadata:", response['metadata'])

# Step 8: Ask another question
response2 = llm.generate("Explain cloud computing", max_tokens=256)
print("\nSecond response:")
print(response2['text'])

# To exit:
exit()
```

---

## ✅ Option 3: Create a Quick Test Script

```bash
# Create the script
cat > /Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen/quick_test.py << 'EOF'
import os
from pathlib import Path

# Load environment
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter

print("=" * 60)
print("🧪 QUICK LLM TEST")
print("=" * 60)

llm = LLMAdapter()

print(f"\n✅ Provider: {llm.provider}")
print(f"✅ Model: {llm.model}")

questions = [
    "What is AI?",
    "Explain blockchain",
    "How does machine learning work?"
]

for i, q in enumerate(questions, 1):
    print(f"\n📝 Question {i}: {q}")
    response = llm.generate(q, max_tokens=150)
    print(f"📖 Answer: {response['text']}\n")
EOF

# Run the script
python3 quick_test.py
```

---

## ✅ Option 4: Test Different Aspects

### Test 1: Check Configuration
```bash
python3 << 'EOF'
import os
from pathlib import Path

env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter

llm = LLMAdapter()

print("Configuration Check:")
print(f"  Provider: {llm.provider}")
print(f"  Model: {llm.model}")
print(f"  Available: {llm.is_available}")
print(f"  Configured: {llm.is_configured()}")
EOF
```

### Test 2: Check Generation
```bash
python3 << 'EOF'
import os
from pathlib import Path

env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter

llm = LLMAdapter()
response = llm.generate("Hello, how are you?", max_tokens=100)

print("Generation Test:")
print(f"  Response: {response['text']}")
print(f"  Length: {len(response['text'])} characters")
print(f"  Provider: {response['metadata']['provider']}")
EOF
```

### Test 3: Multiple Questions
```bash
python3 << 'EOF'
import os
from pathlib import Path

env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter

llm = LLMAdapter()

questions = [
    ("What is 2+2?", 50),
    ("Explain quantum computing", 150),
    ("What are benefits of AI?", 200),
]

for q, tokens in questions:
    print(f"\nQ: {q}")
    response = llm.generate(q, max_tokens=tokens)
    print(f"A: {response['text'][:100]}...")
EOF
```

### Test 4: Error Handling
```bash
python3 << 'EOF'
import os
from pathlib import Path

env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter

try:
    llm = LLMAdapter()
    
    if llm.is_configured():
        response = llm.generate("Test", max_tokens=100)
        print(f"✅ Success: {response['text'][:80]}...")
    else:
        print("❌ LLM not configured")
        
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

---

## 🎯 My Recommended Approach for You

**Step 1**: Start with **Option 2** (Interactive Shell)
```bash
cd /Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen
python3
# Then type the commands from Option 2 above
```

**Step 2**: Try **Option 3** (Quick Test Script)
```bash
python3 quick_test.py
```

**Step 3**: Use **Option 4** (Specific Tests) for debugging
```bash
# Test configuration
python3 << 'EOF'
... (code from Test 1 above)
EOF
```

---

## 🔧 Common Testing Scenarios

### Scenario 1: "I want to see a full response"
```bash
python3 << 'EOF'
import os
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter
llm = LLMAdapter()
response = llm.generate("Explain the concept of machine learning in detail", max_tokens=500)
print(response['text'])
EOF
```

### Scenario 2: "I want to test 5 different questions"
```bash
python3 << 'EOF'
import os
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter
llm = LLMAdapter()

for i, q in enumerate([
    "What is AI?",
    "Explain ML", 
    "Cloud benefits",
    "Blockchain explained",
    "IoT definition"
], 1):
    r = llm.generate(q, max_tokens=100)
    print(f"{i}. {q}\n   → {r['text'][:80]}...\n")
EOF
```

### Scenario 3: "I want to measure response time"
```bash
python3 << 'EOF'
import os
import time
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()

from agents.llm_adapter import LLMAdapter
llm = LLMAdapter()

start = time.time()
response = llm.generate("What is AI?", max_tokens=200)
elapsed = time.time() - start

print(f"Response: {response['text'][:100]}...")
print(f"Time taken: {elapsed:.2f} seconds")
EOF
```

---

## 📋 Quick Command Reference

| What you want | Command |
|---|---|
| **Quick test** | `python3 -c "...code..."` (Option 1) |
| **Interactive** | `python3` then type commands (Option 2) |
| **Save test** | `cat > test.py << 'EOF'` then `python3 test.py` (Option 3) |
| **Measure speed** | Use `time` prefix: `time python3 quick_test.py` |
| **See all output** | Add `max_tokens=500` to generate more |
| **Debug errors** | Add `try/except` block (Test 4) |

---

## 🎉 Now You're Ready!

Pick any option above and test yourself! Here's the simplest start:

```bash
cd /Users/mansidaksingh/Desktop/capestone/enterprise_kb_autogen
python3 << 'EOF'
import os
from pathlib import Path
env_file = Path('.env')
for line in env_file.read_text().split('\n'):
    if line.strip() and not line.startswith('#') and '=' in line:
        key, value = line.split('=', 1)
        os.environ[key.strip()] = value.strip()
from agents.llm_adapter import LLMAdapter
llm = LLMAdapter()
print("Testing LLM...")
print(f"Provider: {llm.provider}")
response = llm.generate("Hello! How are you?", max_tokens=100)
print(f"\nResponse: {response['text']}")
EOF
```

Go try it! 🚀
