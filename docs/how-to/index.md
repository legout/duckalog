# How-to Guides

How-to guides are problem-oriented recipes that help you solve specific tasks with Duckalog. Each guide provides step-by-step solutions to real-world problems.

## What are How-to Guides?

How-to guides differ from tutorials in their focus and approach:

- **Goal-oriented**: Solve specific problems rather than teaching concepts
- **Direct and practical**: Step-by-step solutions without extensive explanation
- **Standalone**: Each guide solves a complete problem independently
- **Assumes basic knowledge**: You understand Duckalog fundamentals

## Popular How-to Guides

### Configuration and Setup

#### [Environment Management](environment-management.md)
Set up and manage different environments (development, staging, production) with proper separation of concerns.

**You'll learn:**
- Environment-specific configuration patterns
- Secure credential management across environments
- Deployment strategies for different contexts
- Docker and Kubernetes integration

**Common problems solved:**
- "How do I manage different database connections for dev vs prod?"
- "How do I keep secrets out of my configuration files?"
- "How do I deploy same config to multiple environments?"

#### [Secrets Persistence](secrets-persistence.md)
Configure and manage secrets persistence with proper security considerations for temporary and persistent storage.

**You'll learn:**
- Differences between temporary and persistent secrets
- Security implications of each approach
- Configuration patterns for optimal secret management
- Best practices for secure credential handling

**Common problems solved:**
- "When should I use persistent vs temporary secrets?"
- "How do I balance security and convenience?"
- "What are the security risks of persistent secrets?"
- "How do I migrate between temporary and persistent secrets?"

#### [Migration from Manual SQL](migration.md)
Migrate existing manual SQL workflows to Duckalog configuration-driven approach.

**You'll learn:**
- Converting existing `CREATE VIEW` statements to Duckalog config
- Preserving business logic during migration
- Incremental migration strategies
- Validation and testing approaches

**Common problems solved:**
- "How do I move from manual SQL files to Duckalog?"
- "How do I ensure my migrated views produce the same results?"
- "How do I migrate a large number of existing views?"

### Performance and Optimization

#### [Performance Tuning](performance-tuning.md)
Optimize Duckalog performance for your specific workload and data characteristics.

**You'll learn:**
- Memory and threading configuration
- Query optimization techniques
- Caching strategies
- Performance monitoring and debugging

**Common problems solved:**
- "How do I make my queries run faster?"
- "How do I handle large datasets efficiently?"
- "How do I optimize memory usage?"

### Development and Debugging

#### [Debugging Build Failures](debugging-builds.md)
Diagnose and resolve common catalog build issues and errors.

**You'll learn:**
- Systematic debugging approaches
- Common error patterns and solutions
- Using diagnostic tools effectively
- Prevention strategies

**Common problems solved:**
- "Why is my catalog build failing?"
- "How do I fix SQL syntax errors in my views?"
- "How do I resolve path and file access issues?"

## How-to vs Tutorials vs Reference

| Type | Purpose | Approach | When to Use |
|-------|---------|-----------|-------------|
| **How-to Guides** | Solve specific problems | Step-by-step recipes | "I need to accomplish X" |
| **Tutorials** | Learn by doing | Comprehensive learning | "I want to learn Y" |
| **Reference** | Technical information | Complete documentation | "I need details about Z" |

## Choosing the Right Guide

### Start Here If You:
- **Have a specific problem**: "I need to set up production configs"
- **Know the basics**: Already understand Duckalog fundamentals
- **Want practical solutions**: Prefer step-by-step instructions
- **Are time-constrained**: Need quick answers to specific issues

### Try Tutorials If You:
- **Are new to Duckalog**: "I'm just getting started"
- **Want comprehensive learning**: "I want to understand the concepts"
- **Have time to learn**: Can invest in deeper understanding
- **Prefer guided learning**: Like structured, progressive content

### Use Reference If You:
- **Need technical details**: "What are all the options for X?"
- **Are looking up specifics**: "How does this function work?"
- **Want complete information**: Need comprehensive coverage
- **Are documenting or integrating**: Building tools or documentation

## Guide Structure

Each how-to guide follows this pattern:

### Problem Statement
Clear description of the problem you're trying to solve.

### Prerequisites
What you need to know or have before starting.

### Solution Steps
Step-by-step instructions to solve the problem.

### Verification
How to confirm the solution works.

### Common Variations
Adaptations for related scenarios.

### Troubleshooting
Common issues and their solutions.

## Contributing How-to Guides

Have a solution to a common Duckalog problem? Consider contributing a how-to guide:

### Good How-to Guide Characteristics:
- **Specific problem**: Solves one well-defined issue
- **Complete solution**: Provides end-to-end steps
- **Tested approach**: Solution has been verified to work
- **Clear structure**: Easy to follow and reproduce
- **Practical focus**: Real-world applicability

### Guide Template:
```markdown
# How to [Solve Specific Problem]

## Problem
Brief description of the problem and when it occurs.

## Prerequisites
What users need before starting.

## Solution
Step-by-step solution with code examples.

## Verification
How to test that it works.

## Variations
Common adaptations and alternatives.

## Troubleshooting
Typical issues and solutions.
```

## Getting Help

If you're stuck on a specific problem:

1. **Search the how-to guides** above for your specific issue
2. **Check the [troubleshooting guide](../guides/troubleshooting.md)** for comprehensive error resolution
3. **Browse [examples](../examples/index.md)** for similar patterns
4. **Consult the [API reference](../reference/api.md)** for technical details
5. **Ask the community** with specific details about your problem

## Next Steps

After solving your immediate problem:

- **Explore related guides** to expand your skills
- **Try tutorials** to deepen your understanding
- **Study reference docs** for comprehensive knowledge
- **Contribute your solutions** to help others

Choose a guide above to solve your specific problem, or explore related topics to build your Duckalog expertise!