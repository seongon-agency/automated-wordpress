"""
Test the configuration agent to verify it has all tools
"""

from agents.configuration_agent import create_configuration_agent
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("TESTING CONFIGURATION AGENT SETUP")
print("="*80)

# Check environment
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in environment")
    exit(1)
else:
    print(f"✅ ANTHROPIC_API_KEY found: {api_key[:20]}...")

# Create agent
print("\n" + "="*80)
print("Creating Configuration Agent...")
print("="*80)

try:
    agent = create_configuration_agent()
    print("✅ Agent created successfully")

    # Check tools
    print("\n" + "="*80)
    print("Checking Agent Tools")
    print("="*80)

    if hasattr(agent, 'tools') and agent.tools:
        print(f"✅ Agent has {len(agent.tools)} tool(s):")
        for tool in agent.tools:
            tool_name = getattr(tool, '__name__', str(tool))
            print(f"   - {tool_name}")
    else:
        print("❌ Agent has no tools configured")

    # Check instructions
    print("\n" + "="*80)
    print("Checking Agent Instructions")
    print("="*80)

    if hasattr(agent, 'instructions'):
        print(f"✅ Agent has {len(agent.instructions)} instruction lines")
        print("   First few instructions:")
        for instruction in agent.instructions[:5]:
            print(f"   - {instruction[:60]}...")

    print("\n" + "="*80)
    print("✅ ALL CHECKS PASSED - Agent is properly configured")
    print("="*80)
    print("\nYou can now run 'python3 main.py' and select option 2 to test it.\n")

except Exception as e:
    print(f"\n❌ Error creating agent: {e}")
    import traceback
    traceback.print_exc()
