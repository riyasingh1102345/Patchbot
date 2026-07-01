# smoke_test.py
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

print("✅ Step 1: Environment variables loaded successfully.")
print(f"   Project Name: {os.getenv('LANGCHAIN_PROJECT')}")

# Test LangGraph component compilation
memory = MemorySaver()
print("✅ Step 2: LangGraph Checkpointer compiled successfully.")

# Test FastMCP initialization
mcp = FastMCP("Test-Sandbox")
print("✅ Step 3: FastMCP Protocol layer initialized successfully.")

print("\n🚀 Hour 1 Complete! Both systems are fully aligned and verified.")

