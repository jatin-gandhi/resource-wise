#!/usr/bin/env python3
"""Simple test runner for realistic QueryAgent tests."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run the realistic query tests with proper setup."""

    # Get the backend directory
    backend_dir = Path(__file__).parent.parent

    # Check if we're in the right directory
    if not (backend_dir / "app").exists():
        print(
            "❌ Error: Could not find app directory. Make sure you're running from the backend directory."
        )
        sys.exit(1)

    # Set up environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)

    # Check for API key
    if not env.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment.")
        print("   The tests will run but skip LLM generation.")
        print("   To run full tests, set OPENAI_API_KEY environment variable.")
        print()

    # Run the test
    test_script = backend_dir / "scripts" / "test_realistic_queries.py"

    try:
        print("🚀 Running realistic QueryAgent tests...")
        print(f"📁 Backend directory: {backend_dir}")
        print(f"🐍 Python path: {env.get('PYTHONPATH')}")
        print()

        result = subprocess.run(
            [sys.executable, str(test_script)], cwd=str(backend_dir), env=env, check=False
        )

        if result.returncode == 0:
            print("\n✅ Tests completed successfully!")
        else:
            print(f"\n❌ Tests failed with exit code: {result.returncode}")

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
