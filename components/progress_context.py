"""
Progress Context Manager
Provides consistent progress indicators and loading states for long operations
"""

import streamlit as st
from contextlib import contextmanager
from typing import Optional
import time


@contextmanager
def loading_spinner(message: str = "Processing...", show_toast_on_complete: bool = False,
                   completion_message: Optional[str] = None):
    """
    Context manager for showing loading spinner during operations

    Usage:
        with loading_spinner("Importing transactions..."):
            # Long running operation
            result = import_csv(file)

        with loading_spinner("Exporting data...", show_toast_on_complete=True,
                            completion_message="Export completed!"):
            export_data()

    Args:
        message: Loading message to display
        show_toast_on_complete: Whether to show toast notification on completion
        completion_message: Custom completion message for toast
    """
    start_time = time.time()

    with st.spinner(message):
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time

            if show_toast_on_complete:
                toast_msg = completion_message or f"Operation completed in {elapsed_time:.1f}s"
                st.toast(toast_msg, icon="✅")


@contextmanager
def progress_tracker(total_items: int, operation_name: str = "Processing"):
    """
    Context manager for tracking progress with a progress bar

    Usage:
        with progress_tracker(len(items), "Importing") as tracker:
            for i, item in enumerate(items):
                process(item)
                tracker.update(i + 1, f"Processing {item.name}...")

    Args:
        total_items: Total number of items to process
        operation_name: Name of the operation for display
    """
    class ProgressTracker:
        def __init__(self, total: int, name: str):
            self.total = total
            self.name = name
            self.progress_bar = st.progress(0)
            self.status_text = st.empty()
            self.start_time = time.time()

        def update(self, current: int, message: Optional[str] = None):
            """Update progress bar and status message"""
            progress = current / self.total if self.total > 0 else 0
            self.progress_bar.progress(min(progress, 1.0))

            if message:
                self.status_text.text(message)
            else:
                elapsed = time.time() - self.start_time
                eta = (elapsed / current * (self.total - current)) if current > 0 else 0
                self.status_text.text(
                    f"{self.name}: {current}/{self.total} ({progress*100:.0f}%) - "
                    f"ETA: {eta:.0f}s"
                )

        def complete(self, message: Optional[str] = None):
            """Mark operation as complete"""
            self.progress_bar.progress(1.0)
            elapsed = time.time() - self.start_time
            completion_msg = message or f"{self.name} completed in {elapsed:.1f}s"
            self.status_text.success(completion_msg)

        def cleanup(self):
            """Clean up progress elements"""
            self.progress_bar.empty()
            self.status_text.empty()

    tracker = ProgressTracker(total_items, operation_name)
    try:
        yield tracker
    finally:
        tracker.cleanup()


def show_operation_status(operation_name: str,
                         items_processed: int,
                         total_items: int,
                         errors: int = 0,
                         warnings: int = 0):
    """
    Display a summary status of a completed operation

    Args:
        operation_name: Name of the operation
        items_processed: Number of items successfully processed
        total_items: Total number of items attempted
        errors: Number of errors encountered
        warnings: Number of warnings encountered
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Processed", f"{items_processed}/{total_items}")

    with col2:
        success_rate = (items_processed / total_items * 100) if total_items > 0 else 0
        st.metric("Success Rate", f"{success_rate:.0f}%")

    with col3:
        if errors > 0:
            st.metric("Errors", errors, delta=f"-{errors}", delta_color="inverse")
        else:
            st.metric("Errors", "0", delta="✓", delta_color="normal")

    with col4:
        if warnings > 0:
            st.metric("Warnings", warnings, delta=f"-{warnings}", delta_color="inverse")
        else:
            st.metric("Warnings", "0", delta="✓", delta_color="normal")


def batch_operation_wrapper(items: list,
                            process_fn: callable,
                            operation_name: str = "Processing",
                            show_progress: bool = True) -> tuple:
    """
    Wrapper for batch operations with automatic progress tracking

    Args:
        items: List of items to process
        process_fn: Function to apply to each item (should return True on success)
        operation_name: Name of operation for display
        show_progress: Whether to show progress bar

    Returns:
        Tuple of (successful_count, error_count, warnings)

    Usage:
        def import_transaction(txn_data):
            # Process transaction
            return True  # or False on error

        success, errors, warnings = batch_operation_wrapper(
            transactions,
            import_transaction,
            "Importing Transactions"
        )
    """
    successful = 0
    errors = 0
    warnings = []

    if show_progress:
        with progress_tracker(len(items), operation_name) as tracker:
            for i, item in enumerate(items):
                try:
                    result = process_fn(item)
                    if result:
                        successful += 1
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
                    warnings.append(str(e))

                tracker.update(i + 1)

            tracker.complete(f"{operation_name} completed: {successful} successful, {errors} errors")
    else:
        for item in items:
            try:
                result = process_fn(item)
                if result:
                    successful += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                warnings.append(str(e))

    return successful, errors, warnings


def show_loading_skeleton(num_rows: int = 3):
    """
    Display a loading skeleton while data is being fetched

    Args:
        num_rows: Number of skeleton rows to display
    """
    for _ in range(num_rows):
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            with col1:
                st.markdown(
                    '<div style="background: #e0e0e0; height: 20px; border-radius: 4px;"></div>',
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    '<div style="background: #e0e0e0; height: 20px; border-radius: 4px;"></div>',
                    unsafe_allow_html=True
                )
            with col3:
                st.markdown(
                    '<div style="background: #e0e0e0; height: 20px; border-radius: 4px;"></div>',
                    unsafe_allow_html=True
                )
            st.markdown("<br>", unsafe_allow_html=True)
