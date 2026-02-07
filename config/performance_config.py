"""
Performance Configuration for Tax Helper

Central configuration for all performance-related settings.
Adjust these values based on your hardware and dataset size.

Author: Tax Helper Development Team
Date: 2025-10-17
"""

# ============================================================================
# PAGINATION SETTINGS
# ============================================================================

PAGINATION = {
    # Default page size for lists
    'default_page_size': 50,

    # Available page size options
    'page_size_options': [25, 50, 100, 200],

    # Maximum items to load at once (safety limit)
    'max_page_size': 500,

    # Show "Load More" or pagination controls
    'use_infinite_scroll': False,

    # Items to load per "Load More" click
    'infinite_scroll_increment': 50,
}


# ============================================================================
# CACHE SETTINGS
# ============================================================================

CACHE_TTL = {
    # Static data (rarely changes)
    'categories': 7200,        # 2 hours
    'income_types': 7200,      # 2 hours
    'merchants': 3600,         # 1 hour
    'rules': 1800,             # 30 minutes

    # Dynamic data (changes frequently)
    'stats': 60,               # 1 minute
    'recent_transactions': 30, # 30 seconds
    'dashboard_data': 120,     # 2 minutes

    # User session data
    'user_preferences': 1800,  # 30 minutes
    'search_results': 300,     # 5 minutes
}

# Cache size limits (number of entries)
CACHE_LIMITS = {
    'max_cache_entries': 1000,
    'cleanup_threshold': 800,  # Start cleanup at this many entries
}


# ============================================================================
# DATABASE SETTINGS
# ============================================================================

DATABASE = {
    # Connection pool settings
    'check_same_thread': False,

    # SQLite PRAGMA settings for performance
    'pragma': {
        'journal_mode': 'WAL',           # Write-Ahead Logging
        'cache_size': -64000,            # 64MB cache
        'mmap_size': 268435456,          # 256MB memory-mapped I/O
        'synchronous': 'NORMAL',         # Balance safety/performance
        'temp_store': 'MEMORY',          # Store temp tables in memory
        'page_size': 4096,               # 4KB pages
    },

    # Query timeout (seconds)
    'timeout': 30,

    # Batch operation sizes
    'batch_insert_size': 1000,
    'batch_update_size': 500,
}


# ============================================================================
# QUERY OPTIMIZATION SETTINGS
# ============================================================================

QUERY_OPTIMIZATION = {
    # Log queries slower than this (seconds)
    'slow_query_threshold': 1.0,

    # Maximum slow queries to keep in memory
    'max_slow_queries_logged': 100,

    # Enable query plan analysis
    'analyze_query_plans': True,

    # Automatically suggest indexes for slow queries
    'suggest_indexes': True,
}


# ============================================================================
# LAZY LOADING SETTINGS
# ============================================================================

LAZY_LOADING = {
    # Maximum items to load at once
    'max_items_per_load': 100,

    # Preload next page in background
    'preload_next_page': True,

    # Cache lazy-loaded data
    'cache_lazy_data': True,
    'lazy_cache_ttl': 600,  # 10 minutes
}


# ============================================================================
# BACKGROUND PROCESSING SETTINGS
# ============================================================================

BACKGROUND_PROCESSING = {
    # Batch size for background operations
    'batch_size': 100,

    # Maximum concurrent background tasks
    'max_concurrent_tasks': 3,

    # Show progress indicators
    'show_progress': True,

    # Background task timeout (seconds)
    'task_timeout': 300,  # 5 minutes
}


# ============================================================================
# MEMORY OPTIMIZATION SETTINGS
# ============================================================================

MEMORY = {
    # Clean session state every N minutes
    'cleanup_interval': 30,

    # Maximum session state size (MB)
    'max_session_size': 100,

    # Use generators for datasets larger than this
    'generator_threshold': 1000,

    # Chunk size for streaming operations
    'stream_chunk_size': 1000,
}


# ============================================================================
# DATA COMPRESSION SETTINGS
# ============================================================================

COMPRESSION = {
    # Compress data larger than this (bytes)
    'compression_threshold': 1024,  # 1KB

    # Compression level (1-9, higher = better compression but slower)
    'compression_level': 6,

    # Enable compression for these data types
    'compress_types': [
        'audit_log',
        'large_json',
        'receipts_metadata',
    ],
}


# ============================================================================
# PERFORMANCE MONITORING SETTINGS
# ============================================================================

MONITORING = {
    # Enable performance monitoring
    'enabled': True,

    # Log performance metrics
    'log_metrics': True,

    # Display performance dashboard
    'show_dashboard': True,

    # Metrics to track
    'track_metrics': [
        'query_time',
        'cache_hits',
        'cache_misses',
        'memory_usage',
        'page_load_time',
    ],

    # Alert thresholds
    'alerts': {
        'slow_query_ms': 1000,
        'high_memory_mb': 500,
        'cache_miss_rate': 0.5,  # 50%
    },
}


# ============================================================================
# STREAMLIT OPTIMIZATION SETTINGS
# ============================================================================

STREAMLIT = {
    # Use st.form() for batch updates
    'use_forms': True,

    # Use st.fragment() for partial updates
    'use_fragments': True,

    # Minimize reruns
    'minimize_reruns': True,

    # Preserve scroll position
    'preserve_scroll': True,

    # Use session state for data persistence
    'use_session_state': True,
}


# ============================================================================
# FEATURE FLAGS
# ============================================================================

FEATURES = {
    # Enable experimental features
    'virtual_scrolling': True,
    'client_caching': True,
    'lazy_loading': True,
    'background_processing': True,
    'data_compression': False,  # Disabled by default
    'query_optimization': True,
    'performance_monitoring': True,
}


# ============================================================================
# HARDWARE-SPECIFIC SETTINGS
# ============================================================================

# Adjust these based on your hardware
HARDWARE = {
    'cpu_cores': 4,
    'memory_gb': 8,
    'storage_type': 'SSD',  # 'SSD' or 'HDD'
}

# Adjust settings based on hardware
if HARDWARE['memory_gb'] < 4:
    # Low memory settings
    DATABASE['pragma']['cache_size'] = -32000  # 32MB
    DATABASE['pragma']['mmap_size'] = 134217728  # 128MB
    PAGINATION['default_page_size'] = 25
    CACHE_LIMITS['max_cache_entries'] = 500

elif HARDWARE['memory_gb'] >= 16:
    # High memory settings
    DATABASE['pragma']['cache_size'] = -128000  # 128MB
    DATABASE['pragma']['mmap_size'] = 536870912  # 512MB
    PAGINATION['default_page_size'] = 100
    CACHE_LIMITS['max_cache_entries'] = 2000


# ============================================================================
# EXPORT SETTINGS
# ============================================================================

def get_all_settings() -> dict:
    """Get all performance settings as a dictionary"""
    return {
        'pagination': PAGINATION,
        'cache_ttl': CACHE_TTL,
        'cache_limits': CACHE_LIMITS,
        'database': DATABASE,
        'query_optimization': QUERY_OPTIMIZATION,
        'lazy_loading': LAZY_LOADING,
        'background_processing': BACKGROUND_PROCESSING,
        'memory': MEMORY,
        'compression': COMPRESSION,
        'monitoring': MONITORING,
        'streamlit': STREAMLIT,
        'features': FEATURES,
        'hardware': HARDWARE,
    }


def print_settings():
    """Print all settings for review"""
    settings = get_all_settings()

    print("\n" + "="*80)
    print("Tax Helper Performance Configuration")
    print("="*80 + "\n")

    for category, values in settings.items():
        print(f"{category.upper().replace('_', ' ')}:")
        for key, value in values.items():
            print(f"  {key}: {value}")
        print()


if __name__ == "__main__":
    print_settings()
