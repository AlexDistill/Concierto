#!/usr/bin/env python3
"""
Brand System Evaluation and Benchmarking
Tests performance, accuracy, and quality of brand generation components
"""

import time
import json
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime

# Import our components
from semantic_analyzer import analyze_semantic
try:
    from deep_source_analyzer import analyze_deep_source
    DEEP_ANALYZER_AVAILABLE = True
except:
    DEEP_ANALYZER_AVAILABLE = False
    
try:
    from vibe_mapper import map_vibe_intensity
    VIBE_MAPPER_AVAILABLE = True
except:
    VIBE_MAPPER_AVAILABLE = False
    
try:
    from brand_translator import translate_source_to_brand
    BRAND_TRANSLATOR_AVAILABLE = True
except:
    BRAND_TRANSLATOR_AVAILABLE = False

class BrandSystemEvaluator:
    """Evaluates and benchmarks the brand generation system"""
    
    def __init__(self):
        self.results = {
            'performance': {},
            'quality': {},
            'consistency': {},
            'errors': [],
            'summary': {}
        }
        
    def evaluate_all_components(self, test_images: List[str] = None) -> Dict:
        """Run complete evaluation suite"""
        
        print("\n" + "="*60)
        print("BRAND SYSTEM EVALUATION")
        print("="*60)
        
        # Get test images
        if not test_images:
            test_images = self._get_test_images()
        
        print(f"\n📊 Testing with {len(test_images)} images...")
        
        # Test each component
        self._evaluate_semantic_analyzer(test_images)
        
        if DEEP_ANALYZER_AVAILABLE:
            self._evaluate_deep_analyzer(test_images)
        else:
            print("⚠️  Deep Analyzer not available for testing")
            
        if VIBE_MAPPER_AVAILABLE:
            self._evaluate_vibe_mapper(test_images)
        else:
            print("⚠️  Vibe Mapper not available for testing")
            
        if BRAND_TRANSLATOR_AVAILABLE:
            self._evaluate_brand_translator(test_images)
        else:
            print("⚠️  Brand Translator not available for testing")
        
        # Test consistency
        self._evaluate_consistency(test_images)
        
        # Generate summary
        self._generate_summary()
        
        # Print results
        self._print_results()
        
        return self.results
    
    def _get_test_images(self) -> List[str]:
        """Get available test images"""
        test_images = []
        
        # Look for images in content directory
        content_dir = Path("content/manual-input/images")
        if content_dir.exists():
            for img_path in content_dir.glob("*.png"):
                test_images.append(str(img_path))
            for img_path in content_dir.glob("*.jpg"):
                test_images.append(str(img_path))
            for img_path in content_dir.glob("*.jpeg"):
                test_images.append(str(img_path))
        
        # Limit to first 5 for quick testing
        return test_images[:5]
    
    def _evaluate_semantic_analyzer(self, test_images: List[str]):
        """Evaluate semantic analyzer performance"""
        print("\n" + "-"*40)
        print("Testing: Semantic Analyzer")
        print("-"*40)
        
        times = []
        successes = 0
        
        for img_path in test_images:
            start_time = time.time()
            try:
                result = analyze_semantic(img_path, "test description")
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if 'error' not in result:
                    successes += 1
                    
                    # Check quality metrics
                    if 'colors' in result:
                        color_count = len(result['colors'].get('most_common', []))
                        if color_count > 0:
                            self.results['quality']['has_colors'] = True
                    
                    if 'visual_properties' in result:
                        self.results['quality']['has_visual_props'] = True
                        
                print(f"✓ {Path(img_path).name}: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"✗ {Path(img_path).name}: {str(e)}")
                self.results['errors'].append({
                    'component': 'semantic_analyzer',
                    'image': img_path,
                    'error': str(e)
                })
        
        # Record performance
        if times:
            self.results['performance']['semantic_analyzer'] = {
                'avg_time': np.mean(times),
                'max_time': max(times),
                'min_time': min(times),
                'success_rate': successes / len(test_images),
                'status': 'fast' if np.mean(times) < 1.0 else 'moderate'
            }
            
            print(f"\nPerformance: Avg {np.mean(times):.2f}s, Success rate: {successes}/{len(test_images)}")
    
    def _evaluate_deep_analyzer(self, test_images: List[str]):
        """Evaluate deep analyzer performance"""
        print("\n" + "-"*40)
        print("Testing: Deep Source Analyzer")
        print("-"*40)
        
        times = []
        successes = 0
        timeout_count = 0
        max_wait = 5.0  # 5 second timeout per image
        
        for img_path in test_images[:2]:  # Test only first 2 due to performance
            start_time = time.time()
            try:
                # Use a simpler approach with timeout
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Analysis timed out")
                
                # Set timeout (Unix only)
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(int(max_wait))
                    
                    result = analyze_deep_source(img_path, "test")
                    
                    signal.alarm(0)  # Cancel alarm
                    
                    elapsed = time.time() - start_time
                    times.append(elapsed)
                    
                    if 'error' not in result:
                        successes += 1
                        
                    print(f"✓ {Path(img_path).name}: {elapsed:.2f}s")
                    
                except TimeoutError:
                    timeout_count += 1
                    print(f"⏱️  {Path(img_path).name}: Timed out after {max_wait}s")
                    
            except Exception as e:
                print(f"✗ {Path(img_path).name}: {str(e)[:50]}...")
                self.results['errors'].append({
                    'component': 'deep_analyzer',
                    'image': img_path,
                    'error': str(e)[:200]
                })
        
        # Record performance
        if times:
            self.results['performance']['deep_analyzer'] = {
                'avg_time': np.mean(times),
                'max_time': max(times),
                'min_time': min(times),
                'success_rate': successes / 2,
                'timeout_rate': timeout_count / 2,
                'status': 'slow' if np.mean(times) > 3.0 else 'moderate'
            }
            print(f"\nPerformance: Avg {np.mean(times):.2f}s, Success: {successes}/2, Timeouts: {timeout_count}")
        else:
            self.results['performance']['deep_analyzer'] = {
                'status': 'failed',
                'timeout_rate': 1.0
            }
            print(f"\n⚠️  All tests timed out or failed")
    
    def _evaluate_vibe_mapper(self, test_images: List[str]):
        """Evaluate vibe mapper performance"""
        print("\n" + "-"*40)
        print("Testing: Vibe Mapper")
        print("-"*40)
        
        times = []
        successes = 0
        
        for img_path in test_images[:3]:  # Test first 3
            start_time = time.time()
            try:
                # Quick timeout mechanism
                result = map_vibe_intensity(img_path, "test vibe")
                elapsed = time.time() - start_time
                
                if elapsed > 10:  # Skip if taking too long
                    print(f"⏱️  {Path(img_path).name}: Taking too long, skipping...")
                    continue
                    
                times.append(elapsed)
                
                if 'error' not in result:
                    successes += 1
                    
                    # Check quality
                    if 'vibe_spectrum' in result:
                        self.results['quality']['has_vibe_spectrum'] = True
                    if 'brand_personality_mapping' in result:
                        self.results['quality']['has_personality'] = True
                        
                print(f"✓ {Path(img_path).name}: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"✗ {Path(img_path).name}: {str(e)[:50]}...")
                self.results['errors'].append({
                    'component': 'vibe_mapper',
                    'image': img_path,
                    'error': str(e)[:200]
                })
        
        # Record performance
        if times:
            self.results['performance']['vibe_mapper'] = {
                'avg_time': np.mean(times),
                'max_time': max(times),
                'min_time': min(times),
                'success_rate': successes / 3,
                'status': 'slow' if np.mean(times) > 5.0 else 'moderate'
            }
            print(f"\nPerformance: Avg {np.mean(times):.2f}s, Success rate: {successes}/3")
    
    def _evaluate_brand_translator(self, test_images: List[str]):
        """Evaluate brand translator performance"""
        print("\n" + "-"*40)
        print("Testing: Brand Translator")
        print("-"*40)
        
        times = []
        successes = 0
        
        for img_path in test_images[:2]:  # Test first 2 due to complexity
            start_time = time.time()
            try:
                # Quick test with timeout
                result = translate_source_to_brand(img_path, "test brand")
                elapsed = time.time() - start_time
                
                if elapsed > 15:  # Skip if taking too long
                    print(f"⏱️  {Path(img_path).name}: Taking too long, skipping...")
                    continue
                    
                times.append(elapsed)
                
                if 'error' not in result:
                    successes += 1
                    
                    # Check quality
                    if 'brand_concept' in result:
                        self.results['quality']['has_brand_concept'] = True
                    if 'color_system' in result:
                        self.results['quality']['has_color_system'] = True
                    if 'brand_voice' in result:
                        self.results['quality']['has_brand_voice'] = True
                        
                print(f"✓ {Path(img_path).name}: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"✗ {Path(img_path).name}: {str(e)[:50]}...")
                self.results['errors'].append({
                    'component': 'brand_translator',
                    'image': img_path,
                    'error': str(e)[:200]
                })
        
        # Record performance
        if times:
            self.results['performance']['brand_translator'] = {
                'avg_time': np.mean(times),
                'max_time': max(times),
                'min_time': min(times),
                'success_rate': successes / 2,
                'status': 'very_slow' if np.mean(times) > 10.0 else 'slow'
            }
            print(f"\nPerformance: Avg {np.mean(times):.2f}s, Success rate: {successes}/2")
    
    def _evaluate_consistency(self, test_images: List[str]):
        """Evaluate consistency of results"""
        print("\n" + "-"*40)
        print("Testing: Consistency")
        print("-"*40)
        
        if len(test_images) < 1:
            print("No images to test consistency")
            return
            
        # Test same image multiple times
        test_image = test_images[0]
        results = []
        
        print(f"Testing consistency with: {Path(test_image).name}")
        
        for i in range(3):
            try:
                result = analyze_semantic(test_image, "consistency test")
                if 'error' not in result and 'colors' in result:
                    primary_color = result['colors']['most_common'][0]['hex'] if result['colors']['most_common'] else None
                    results.append(primary_color)
            except:
                pass
        
        # Check if results are consistent
        if len(results) >= 2:
            consistency = len(set(results)) == 1  # All same
            self.results['consistency']['color_extraction'] = consistency
            
            if consistency:
                print(f"✓ Color extraction is consistent")
            else:
                print(f"⚠️  Color extraction varies: {results}")
        
        # Test vibe consistency
        if VIBE_MAPPER_AVAILABLE and len(test_images) > 0:
            vibe_results = []
            for i in range(2):
                try:
                    result = map_vibe_intensity(test_image, "consistency test")
                    if 'vibe_spectrum' in result:
                        signature = result['vibe_spectrum'].get('vibe_signature', '')
                        vibe_results.append(signature)
                except:
                    pass
            
            if len(vibe_results) >= 2:
                vibe_consistency = len(set(vibe_results)) == 1
                self.results['consistency']['vibe_mapping'] = vibe_consistency
                
                if vibe_consistency:
                    print(f"✓ Vibe mapping is consistent")
                else:
                    print(f"⚠️  Vibe mapping varies")
    
    def _generate_summary(self):
        """Generate evaluation summary"""
        
        # Performance summary
        perf_scores = []
        for component, metrics in self.results['performance'].items():
            if 'avg_time' in metrics:
                # Score based on speed (faster = higher score)
                if metrics['avg_time'] < 1:
                    score = 100
                elif metrics['avg_time'] < 3:
                    score = 80
                elif metrics['avg_time'] < 5:
                    score = 60
                elif metrics['avg_time'] < 10:
                    score = 40
                else:
                    score = 20
                    
                # Adjust for success rate
                if 'success_rate' in metrics:
                    score *= metrics['success_rate']
                    
                perf_scores.append(score)
        
        # Quality summary
        quality_score = sum(1 for v in self.results['quality'].values() if v) / max(1, len(self.results['quality'])) * 100
        
        # Consistency summary
        consistency_score = sum(1 for v in self.results['consistency'].values() if v) / max(1, len(self.results['consistency'])) * 100
        
        # Error rate
        error_rate = len(self.results['errors']) / max(1, sum(len(self.results['performance']) * 3))  # Approximate total tests
        
        self.results['summary'] = {
            'performance_score': np.mean(perf_scores) if perf_scores else 0,
            'quality_score': quality_score,
            'consistency_score': consistency_score,
            'error_rate': error_rate,
            'overall_grade': self._calculate_grade(np.mean(perf_scores) if perf_scores else 0, quality_score, consistency_score, error_rate)
        }
    
    def _calculate_grade(self, perf: float, quality: float, consistency: float, error_rate: float) -> str:
        """Calculate overall grade"""
        # Weighted average
        overall = (perf * 0.4 + quality * 0.3 + consistency * 0.2 + (1 - error_rate) * 100 * 0.1)
        
        if overall >= 90:
            return 'A'
        elif overall >= 80:
            return 'B'
        elif overall >= 70:
            return 'C'
        elif overall >= 60:
            return 'D'
        else:
            return 'F'
    
    def _print_results(self):
        """Print evaluation results"""
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        
        # Performance
        print("\n📊 Performance Metrics:")
        for component, metrics in self.results['performance'].items():
            if 'avg_time' in metrics:
                print(f"  {component}:")
                print(f"    - Average time: {metrics['avg_time']:.2f}s")
                print(f"    - Status: {metrics['status']}")
                if 'success_rate' in metrics:
                    print(f"    - Success rate: {metrics['success_rate']:.1%}")
        
        # Quality
        print("\n✨ Quality Checks:")
        for check, passed in self.results['quality'].items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}")
        
        # Consistency
        if self.results['consistency']:
            print("\n🔄 Consistency:")
            for check, consistent in self.results['consistency'].items():
                status = "✓" if consistent else "⚠️"
                print(f"  {status} {check}")
        
        # Errors
        if self.results['errors']:
            print(f"\n⚠️  Errors: {len(self.results['errors'])} encountered")
        
        # Summary
        print("\n" + "-"*40)
        print("SUMMARY")
        print("-"*40)
        
        summary = self.results['summary']
        print(f"Performance Score: {summary['performance_score']:.1f}/100")
        print(f"Quality Score: {summary['quality_score']:.1f}/100")
        print(f"Consistency Score: {summary['consistency_score']:.1f}/100")
        print(f"Error Rate: {summary['error_rate']:.1%}")
        print(f"\n🎯 Overall Grade: {summary['overall_grade']}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        self._print_recommendations()
    
    def _print_recommendations(self):
        """Print optimization recommendations"""
        
        recommendations = []
        
        # Check performance issues
        for component, metrics in self.results['performance'].items():
            if 'status' in metrics:
                if metrics['status'] in ['slow', 'very_slow']:
                    recommendations.append(f"Optimize {component} - currently {metrics['status']}")
                if 'timeout_rate' in metrics and metrics['timeout_rate'] > 0.5:
                    recommendations.append(f"Fix timeout issues in {component}")
        
        # Check quality issues
        if not self.results['quality']:
            recommendations.append("Improve quality output generation")
        
        # Check consistency issues
        for check, consistent in self.results['consistency'].items():
            if not consistent:
                recommendations.append(f"Improve consistency in {check}")
        
        # Check error rate
        if self.results['summary']['error_rate'] > 0.2:
            recommendations.append("Reduce error rate with better error handling")
        
        if recommendations:
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("  • System performing well!")
    
    def save_results(self, filename: str = "evaluation_results.json"):
        """Save evaluation results to file"""
        with open(filename, 'w') as f:
            # Convert numpy types for JSON serialization
            clean_results = json.loads(json.dumps(self.results, default=str))
            json.dump(clean_results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")


def run_evaluation():
    """Run complete evaluation"""
    evaluator = BrandSystemEvaluator()
    results = evaluator.evaluate_all_components()
    evaluator.save_results()
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test with fewer images
        evaluator = BrandSystemEvaluator()
        test_images = evaluator._get_test_images()[:2]
        results = evaluator.evaluate_all_components(test_images)
    else:
        # Full evaluation
        results = run_evaluation()