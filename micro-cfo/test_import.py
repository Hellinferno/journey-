"""Quick test to verify ComplianceAuditor import"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing import...")
from app.compliance import ComplianceAuditor

print("✅ Import successful!")

# Check if audit_invoice method exists
auditor = ComplianceAuditor()
print(f"✅ ComplianceAuditor instantiated")
print(f"✅ Has audit_invoice method: {hasattr(auditor, 'audit_invoice')}")
print(f"✅ Method type: {type(getattr(auditor, 'audit_invoice', None))}")

# List all methods
print(f"\nAll methods: {[m for m in dir(auditor) if not m.startswith('_')]}")
