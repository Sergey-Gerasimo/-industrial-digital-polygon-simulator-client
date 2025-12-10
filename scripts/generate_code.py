#!/usr/bin/env python3
"""Generate Python code from .proto file."""

import subprocess
import sys
from pathlib import Path


def generate_proto_code():
    """Generate Python code from simulator.proto."""
    proto_file = Path("simulator.proto")
    output_dir = Path("src/simulation_client/proto")

    if not proto_file.exists():
        print(f"Error: {proto_file} not found")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python3",
        "-m",
        "grpc_tools.protoc",
        f"-I.",
        f"--python_out={output_dir}",
        f"--pyi_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file),
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Successfully generated Python code from .proto file")

        # Fix imports
        fix_imports(output_dir)
        create_proto_init(output_dir)

    except subprocess.CalledProcessError as e:
        print(f"Error generating proto code: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)


def fix_imports(output_dir: Path):
    """Fix import statements in generated files."""
    grpc_file = output_dir / "simulator_pb2_grpc.py"

    if not grpc_file.exists():
        return

    content = grpc_file.read_text()
    fixed_content = content.replace(
        "import simulator_pb2 as simulator__pb2",
        "from . import simulator_pb2 as simulator__pb2",
    )

    grpc_file.write_text(fixed_content)
    print(f"Fixed imports in {grpc_file}")


def create_proto_init(output_dir: Path):
    """Create __init__.py for proto module."""
    init_file = output_dir / "__init__.py"

    init_content = '''"""
Generated protobuf and gRPC code.
This module is auto-generated from simulator.proto file.
"""

from .simulator_pb2 import *
from .simulator_pb2_grpc import *

__all__ = [
    "simulator_pb2",
    "simulator_pb2_grpc",
]
'''

    init_file.write_text(init_content)
    print(f"Created {init_file}")


if __name__ == "__main__":
    generate_proto_code()
