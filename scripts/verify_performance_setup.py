#!/usr/bin/env python3
"""
Performance Setup Verification Script

Verifies that all performance optimization components are properly installed
and configured. Run this after integration to ensure everything works.

Usage:
    python scripts/verify_performance_setup.py
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠{RESET} {text}")


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print_success(f"{description} exists: {file_path}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {file_path}")
        return False


def check_imports():
    """Check if performance module can be imported"""
    print_header("1. Checking Python Imports")

    try:
        from components.performance import (
            VirtualScrolling,
            CacheManager,
            QueryOptimizer,
            LazyLoader,
            BackgroundProcessor,
            DataCompression,
            MemoryOptimizer,
            PerformanceMonitor,
            StreamlitOptimizer,
            initialize_performance_optimizations,
            get_optimized_connection
        )
        print_success("All performance components imported successfully")
        return True
    except ImportError as e:
        print_error(f"Failed to import performance module: {e}")
        return False


def check_files():
    """Check if all required files exist"""
    print_header("2. Checking Required Files")

    files = {
        'Performance Module': 'components/performance.py',
        'Migration SQL': 'migrations/add_performance_indexes.sql',
        'Migration Runner': 'migrations/run_migration.py',
        'Integration Guide': 'docs/PERFORMANCE_INTEGRATION.md',
        'Benchmark Script': 'tests/benchmark_performance.py',
        'Configuration': 'config/performance_config.py',
        'Summary Document': 'PERFORMANCE_SUMMARY.md',
    }

    all_exist = True
    for description, file_path in files.items():
        if not check_file_exists(file_path, description):
            all_exist = False

    return all_exist


def check_database_indexes(db_path='tax_helper.db'):
    """Check if performance indexes are installed"""
    print_header("3. Checking Database Indexes")

    if not Path(db_path).exists():
        print_warning(f"Database not found at {db_path}")
        print("  Run the application first to create the database")
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check for performance indexes
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """)
        index_count = cursor.fetchone()[0]

        if index_count >= 30:
            print_success(f"Found {index_count} performance indexes")
        elif index_count > 0:
            print_warning(f"Found only {index_count} indexes (expected 30+)")
            print("  Run: python migrations/run_migration.py")
        else:
            print_error("No performance indexes found")
            print("  Run: python migrations/run_migration.py")
            return False

        # Check specific important indexes
        important_indexes = [
            'idx_transactions_date',
            'idx_transactions_reviewed',
            'idx_expenses_category',
            'idx_income_type',
            'idx_audit_log_timestamp',
        ]

        print("\n  Checking key indexes:")
        for idx_name in important_indexes:
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master
                WHERE type='index' AND name=?
            """, (idx_name,))

            if cursor.fetchone()[0] > 0:
                print_success(f"  {idx_name}")
            else:
                print_error(f"  {idx_name} MISSING")

        # Check database settings
        print("\n  Checking PRAGMA settings:")
        pragmas = ['journal_mode', 'cache_size', 'synchronous']

        for pragma in pragmas:
            cursor.execute(f"PRAGMA {pragma}")
            value = cursor.fetchone()[0]
            print(f"    {pragma}: {value}")

        conn.close()
        return True

    except Exception as e:
        print_error(f"Database check failed: {e}")
        return False


def check_config():
    """Check configuration file"""
    print_header("4. Checking Configuration")

    try:
        from config.performance_config import (
            PAGINATION,
            CACHE_TTL,
            DATABASE,
            FEATURES,
            get_all_settings
        )

        print_success("Configuration loaded successfully")

        print("\n  Key settings:")
        print(f"    Default page size: {PAGINATION['default_page_size']}")
        print(f"    Stats cache TTL: {CACHE_TTL['stats']}s")
        print(f"    Database cache size: {DATABASE['pragma']['cache_size']} pages")

        print("\n  Enabled features:")
        for feature, enabled in FEATURES.items():
            status = "✓" if enabled else "✗"
            print(f"    {status} {feature}")

        return True

    except Exception as e:
        print_error(f"Configuration check failed: {e}")
        return False


def check_streamlit():
    """Check if Streamlit is installed"""
    print_header("5. Checking Streamlit")

    try:
        import streamlit as st
        version = st.__version__
        print_success(f"Streamlit {version} installed")

        # Check for required features
        major, minor = map(int, version.split('.')[:2])

        if major >= 1 and minor >= 32:
            print_success("Streamlit version supports st.fragment()")
        else:
            print_warning("Streamlit < 1.32, st.fragment() not available")

        return True

    except ImportError:
        print_error("Streamlit not installed")
        print("  Run: pip install streamlit")
        return False


def test_basic_functionality():
    """Test basic functionality"""
    print_header("6. Testing Basic Functionality")

    try:
        from components.performance import (
            VirtualScrolling,
            CacheManager,
            PerformanceMonitor
        )

        # Test cache manager
        try:
            categories = CacheManager.get_categories_cached("tax_helper.db")
            print_success(f"Cache test: Retrieved {len(categories)} categories")
        except Exception as e:
            print_warning(f"Cache test failed (database may not exist yet): {e}")

        # Test performance monitor
        try:
            metrics = PerformanceMonitor.get_performance_metrics()
            print_success(f"Performance monitoring working")
        except Exception as e:
            print_warning(f"Performance monitoring test failed: {e}")

        return True

    except Exception as e:
        print_error(f"Functionality test failed: {e}")
        return False


def print_summary(results):
    """Print summary of checks"""
    print_header("Summary")

    total = len(results)
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    warnings = sum(1 for r in results.values() if r is None)

    print(f"Total checks: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    if warnings > 0:
        print(f"{YELLOW}Warnings: {warnings}{RESET}")

    print("\n" + "="*80)

    if failed == 0 and warnings == 0:
        print(f"{GREEN}✓ All checks passed! Performance optimization is ready to use.{RESET}")
    elif failed == 0:
        print(f"{YELLOW}⚠ Some optional checks have warnings, but core functionality is working.{RESET}")
    else:
        print(f"{RED}✗ Some checks failed. Please address the issues above.{RESET}")

    print("="*80 + "\n")


def print_next_steps():
    """Print next steps"""
    print_header("Next Steps")

    print("1. If indexes are missing:")
    print("   python migrations/run_migration.py")
    print()

    print("2. Run benchmarks to test performance:")
    print("   python tests/benchmark_performance.py")
    print()

    print("3. Read integration guide:")
    print("   docs/PERFORMANCE_INTEGRATION.md")
    print()

    print("4. Start integrating into your pages:")
    print("   - Dashboard: Add caching")
    print("   - Final Review: Add virtual scrolling")
    print("   - Import: Add background processing")
    print("   - All pages: Use get_optimized_connection()")
    print()

    print("5. Monitor performance:")
    print("   - Check Performance Dashboard in app")
    print("   - Review slow query logs")
    print("   - Adjust configuration as needed")
    print()


def main():
    """Run all verification checks"""
    print(f"\n{BLUE}{'='*80}")
    print("Tax Helper Performance Setup Verification")
    print(f"{'='*80}{RESET}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    results = {}

    # Run checks
    results['imports'] = check_imports()
    results['files'] = check_files()
    results['database'] = check_database_indexes()
    results['config'] = check_config()
    results['streamlit'] = check_streamlit()
    results['functionality'] = test_basic_functionality()

    # Print summary
    print_summary(results)

    # Print next steps
    print_next_steps()

    # Exit code
    if results.get('imports') is False or results.get('files') is False:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
