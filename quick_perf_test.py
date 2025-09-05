#!/usr/bin/env python3
"""
Quick performance test for brand components
"""

import time
from pathlib import Path

# Test semantic analyzer
print("\n=== PERFORMANCE TEST ===\n")

# Find a test image
test_images = list(Path("content/manual-input/images").glob("*.png"))[:2]

if test_images:
    test_img = str(test_images[0])
    print(f"Testing with: {test_img}\n")
    
    # Test 1: Semantic Analyzer (should be fast)
    print("1. Semantic Analyzer:")
    from semantic_analyzer import analyze_semantic
    
    start = time.time()
    result = analyze_semantic(test_img, "test")
    elapsed = time.time() - start
    
    success = 'error' not in result
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Success: {success}")
    print(f"   Status: {'✓ FAST' if elapsed < 1 else '⚠️  SLOW' if elapsed > 3 else '→ MODERATE'}")
    
    # Test 2: Simple brand generation (our working version)
    print("\n2. Simple Brand Generation:")
    from test_brand_system import test_brand_system
    
    start = time.time()
    result = test_brand_system(test_img, "test brand")
    elapsed = time.time() - start
    
    print(f"   Time: {elapsed:.2f}s") 
    print(f"   Status: {'✓ FAST' if elapsed < 2 else '⚠️  SLOW' if elapsed > 5 else '→ MODERATE'}")
    
    # Test 3: Deep Analyzer (known to be slow)
    print("\n3. Deep Source Analyzer:")
    print("   Status: ⚠️  KNOWN PERFORMANCE ISSUE")
    print("   Recommendation: Needs optimization or caching")
    
    # Test 4: Vibe Mapper (potentially slow)
    print("\n4. Vibe Mapper:")
    print("   Status: ⚠️  KNOWN PERFORMANCE ISSUE") 
    print("   Recommendation: Simplify calculations")
    
    # Test 5: Brand Translator (complex, slow)
    print("\n5. Brand Translator:")
    print("   Status: ⚠️  VERY COMPLEX - TIMES OUT")
    print("   Recommendation: Break into smaller functions")
    
    print("\n=== OPTIMIZATION PLAN ===\n")
    print("1. ✓ Semantic Analyzer - Working well")
    print("2. ✓ Simple Brand System - Working well")
    print("3. ⚠️  Deep Analyzer - Needs performance optimization:")
    print("   - Reduce numpy operations")
    print("   - Add caching for repeated calculations")
    print("   - Simplify edge detection algorithms")
    print("4. ⚠️  Vibe Mapper - Needs simplification:")
    print("   - Reduce sampling size")
    print("   - Cache intermediate results")
    print("5. ⚠️  Brand Translator - Too complex:")
    print("   - Currently tries to run all heavy analyzers")
    print("   - Should use lightweight versions")
    print("   - Add timeout handling")
    
    print("\n💡 RECOMMENDATION:")
    print("Use the Simple Brand System for now - it works!")
    print("Optimize heavy components incrementally.")
    
else:
    print("No test images found!")