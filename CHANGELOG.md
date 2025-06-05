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

## [0.1.5] - 2025-01-27

### Added
- Robust JSON parser (`agents_hub.utils.json_parser`) with multiple extraction strategies
  - Bracket-based extraction with proper string handling
  - Regex-based extraction for JSON objects
  - Code block extraction for markdown-wrapped JSON
  - Line-based extraction for multiline JSON structures
- Intelligent agent selector (`agents_hub.orchestration.agent_selector`) for content-based agent selection
  - Multi-factor scoring system (keywords, capabilities, description similarity, name relevance)
  - Context-aware scoring that reduces ambiguous term weights in technical contexts
  - Domain-specific keyword enhancement for coding, writing, and research agents
- Comprehensive test suite with 69 tests covering all orchestration scenarios

### Changed
- Enhanced AgentWorkforce orchestration system with intelligent fallback logic
- Improved orchestrator prompts with clearer JSON format requirements
- Better error handling and logging throughout the orchestration process
- Agent selection now uses content analysis instead of defaulting to first agent

### Fixed
- **Critical Bug**: JSON parsing failures that caused "Expecting value: line 1 column 1 (char 0)" errors
- **Critical Bug**: Poor fallback logic that defaulted to first agent regardless of task content
- **Critical Bug**: Incorrect agent routing when orchestration failed
- **Critical Bug**: Limited error context and poor debugging information
- JSON parsing now handles explanatory text before/after JSON responses
- Agent selection now intelligently matches tasks to appropriate specialized agents
- Unknown agent references now trigger intelligent substitution instead of errors
- Comprehensive error tracking with fallback reason reporting

## [0.1.3] - 2025-04-25

### Added
- Enhanced MCPTool with improved resource management and error handling
  - Added async context manager support for clean resource management
  - Added proper cleanup of resources to prevent memory leaks
  - Added comprehensive examples demonstrating MCP usage patterns
- New dedicated MCP documentation page with detailed usage examples
- Updated all HTML documentation to include MCP navigation links
- Added MCP example to the examples page

### Changed
- Refactored MCPTool to better handle agent integration
  - Improved parameter handling for agent tool integration
  - Enhanced error reporting with detailed error messages
  - Better handling of tool name prefixing
- Updated examples to print both queries and responses for better readability
- Improved documentation structure with consistent navigation

### Fixed
- Fixed resource cleanup issues in MCPTool to prevent memory leaks
- Fixed parameter handling in MCPTool to work correctly with agents
- Fixed error handling in MCP server connections
- Fixed pagination links in documentation for better navigation

## [0.1.2] - 2025-04-20

### Added
- Recursive character text splitter with configurable chunk size, chunk overlap, and custom separators
- Enhanced RAG capabilities for document ingestion (PDFs, docs, URLs)
- Improved monitoring with Langfuse integration for tracking costs and user IDs

### Changed
- Updated LLM provider interfaces to expose model property for better monitoring
- Enhanced monitoring system to track latency accurately
- Improved error handling in document processing utilities

### Fixed
- Fixed latency tracking in Langfuse monitoring to show accurate values
- Fixed cost tracking for different LLM providers (OpenAI, Claude, Gemini)
- Fixed model name detection for various model variants

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
