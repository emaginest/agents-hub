# Changelog

All notable changes to the Agents Hub framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Coding module with specialized agents for software development
  - Project Manager Agent
  - Analyst Agent
  - Backend Developer Agent
  - Frontend Developer Agent
  - DevOps Engineer Agent
  - Security Engineer Agent
  - QA Tester Agent
- Coding tools for software development
  - Git Tool with human approval for critical operations
  - AWS CDK Tool with human approval for deployments
  - Code Generator Tool
  - Code Analyzer Tool
  - Testing Tool
- CodingWorkforce class for coordinating specialized coding agents
- Human approval interface for critical operations
- Code templates for FastAPI, React, and AWS CDK
- Comprehensive documentation for all modules
- Example applications demonstrating framework capabilities

### Changed
- Improved project structure for better organization and clarity
- Enhanced documentation with detailed README files for each module
- Updated examples to use the new module structure

### Fixed
- Removed duplicate and obsolete code
- Cleaned up temporary and generated files
- Fixed import statements to reflect the new structure

## [0.1.1] - 2025-04-17

### Added
- InMemoryMemory implementation for simple in-memory storage
- New memory_example demonstrating long-term memory with PostgreSQL
- Docker support for local memory testing with PostgreSQL
- Interactive memory commands (stats, history, search) in memory example
- Support for continuing conversations across sessions with conversation IDs

### Changed
- Updated memory module to expose both PostgreSQL and InMemory backends
- Improved memory interface with consistent method signatures
- Enhanced documentation for memory systems

### Fixed
- Fixed context handling in Agent.run() method for conversation IDs
- Added optional python-Levenshtein dependency to address fuzzywuzzy warning

## [0.1.0] - 2025-04-03

### Added
- Initial release of the Agents Hub framework
- Multi-agent orchestration capabilities
- Support for multiple LLM providers (OpenAI, Claude, Gemini, Ollama)
- Content moderation system
- Web scraping and search capabilities
- Document processing utilities
- RAG capabilities with PostgreSQL/pgvector
- Model Context Protocol (MCP) integration
- Monitoring and analytics with Langfuse
- Cognitive architecture with metacognitive capabilities
- Memory system with multiple backend options
- Dynamic task routing and agent collaboration
- Example applications demonstrating framework capabilities
