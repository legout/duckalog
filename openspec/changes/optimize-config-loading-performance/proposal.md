# Change: Optimize Configuration Loading Performance

## Why
The configuration loading system has several performance bottlenecks that impact user experience:
- **Double file parsing**: Config files are parsed twice (once for env_files extraction, once for processing)
- **O(K²) validation**: During import processing, validation runs after each merge creating quadratic complexity
- **Repeated path resolution**: Same paths resolved multiple times within single load operation
- **Synchronous I/O**: Import and SQL file loading blocks execution unnecessarily

These issues cause significant delays for configurations with many imports or large file trees. Optimization will improve performance by **30%+** for complex configurations while maintaining all functionality.

## What Changes
- **ELIMINATE**: Double file parsing through single-pass processing
- **OPTIMIZE**: Validation to single pass after all merges complete
- **IMPLEMENT**: Path caching within load operation context  
- **ADD**: Parallel I/O for import and SQL file loading
- **CREATE**: Performance monitoring and benchmarking

## Impact
- **Affected specs**: config
- **Affected code**: `src/duckalog/config/loader.py` (optimization focus), import processing, path resolution
- **Performance**: 30%+ improvement for complex configurations
- **Risk**: Medium (performance changes require careful testing)
- **User benefit**: Faster configuration loading, better developer experience
