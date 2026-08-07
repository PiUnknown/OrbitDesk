import argparse
import json
import time
from src.graph import run_query

parser = argparse.ArgumentParser(description="OrbitDesk local-first support agent")
parser.add_argument("query")
args = parser.parse_args(); started = time.perf_counter(); result = run_query(args.query)
print(result["final_output"]["answer"])
print("\nStructured JSON:\n" + json.dumps(result["final_output"], indent=2))
print("\nTrace:\n" + "\n".join(result["logs"]))
print(f"Question latency: {time.perf_counter() - started:.2f}s")
