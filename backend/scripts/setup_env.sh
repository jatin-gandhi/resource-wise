#!/bin/bash

# =============================================================================
# RESOURCE WISE - LOCAL ENVIRONMENT SETUP SCRIPT
# =============================================================================
# This script sets up environment variables from env.template for local development
# Usage: source scripts/setup_env.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Resource Wise - Environment Setup${NC}"
echo "=================================================="

# Get the backend directory (parent of scripts directory)
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_TEMPLATE="$BACKEND_DIR/env.template"
ENV_FILE="$BACKEND_DIR/.env"

echo -e "${BLUE}📁 Backend Directory: ${NC}$BACKEND_DIR"

# Check if env.template exists
if [[ ! -f "$ENV_TEMPLATE" ]]; then
    echo -e "${RED}❌ Error: env.template not found at $ENV_TEMPLATE${NC}"
    return 1 2>/dev/null || exit 1
fi

echo -e "${GREEN}✅ Found env.template${NC}"

# Function to set environment variable from template
set_env_var() {
    local line="$1"
    
    # Skip comments and empty lines
    if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*$ ]]; then
        return 0
    fi
    
    # Skip section headers (lines with only = characters)
    if [[ "$line" =~ ^[[:space:]]*=+[[:space:]]*$ ]]; then
        return 0
    fi
    
    # Extract key=value pairs
    if [[ "$line" =~ ^[[:space:]]*([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
        local key="${BASH_REMATCH[1]}"
        local value="${BASH_REMATCH[2]}"
        
        # Handle special cases for local development
        case "$key" in
            "OPENAI_API_KEY")
                if [[ "$value" == "sk-your-openai-api-key-here" ]]; then
                    echo -e "${YELLOW}⚠️  Warning: OPENAI_API_KEY is using template value${NC}"
                    echo -e "${YELLOW}   Set your actual API key for full functionality${NC}"
                    # Don't set the template value
                    return 0
                fi
                ;;
            "DEBUG")
                value="true"  # Force debug mode for local development
                ;;
            "DATABASE_ECHO")
                value="false"  # Keep database echo off by default
                ;;
        esac
        
        # Set the environment variable
        export "$key"="$value"
        echo -e "${GREEN}✓${NC} $key=${value}"
    fi
}

echo -e "\n${BLUE}🔧 Setting environment variables...${NC}"

# Read env.template line by line and set variables
while IFS= read -r line; do
    set_env_var "$line"
done < "$ENV_TEMPLATE"

# Check if .env file exists and offer to load it
if [[ -f "$ENV_FILE" ]]; then
    echo -e "\n${BLUE}📄 Found .env file${NC}"
    echo -e "${YELLOW}💡 Loading additional variables from .env...${NC}"
    
    # Parse .env file safely (handle spaces in values)
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*$ ]]; then
            continue
        fi
        
        # Skip section headers
        if [[ "$line" =~ ^[[:space:]]*=+[[:space:]]*$ ]]; then
            continue
        fi
        
        # Extract key=value pairs (handle quoted values)
        if [[ "$line" =~ ^[[:space:]]*([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # Remove surrounding quotes if present
            if [[ "$value" =~ ^\"(.*)\"$ ]] || [[ "$value" =~ ^\'(.*)\'$ ]]; then
                value="${BASH_REMATCH[1]}"
            fi
            
            # Set the environment variable
            export "$key"="$value"
            echo -e "${GREEN}✓${NC} $key (from .env)"
        fi
    done < "$ENV_FILE"
    
    echo -e "${GREEN}✅ Loaded .env file${NC}"
fi

# Validate critical environment variables
echo -e "\n${BLUE}🔍 Validating environment...${NC}"

# Check database connection
if [[ -n "$DB_HOST" && -n "$DB_PORT" && -n "$DB_USER" && -n "$DB_NAME" ]]; then
    echo -e "${GREEN}✓${NC} Database configuration: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
else
    echo -e "${RED}❌ Incomplete database configuration${NC}"
fi

# Check OpenAI API key
if [[ -n "$OPENAI_API_KEY" && "$OPENAI_API_KEY" != "sk-your-openai-api-key-here" ]]; then
    echo -e "${GREEN}✓${NC} OpenAI API key configured"
else
    echo -e "${YELLOW}⚠️  OpenAI API key not configured (tests will run in mock mode)${NC}"
fi

# Set Python path for imports
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
echo -e "${GREEN}✓${NC} Python path: $PYTHONPATH"

echo -e "\n${GREEN}🎉 Environment setup complete!${NC}"
echo -e "\n${BLUE}💡 Usage examples:${NC}"
echo -e "   ${GREEN}# Run realistic query tests${NC}"
echo -e "   python scripts/test_realistic_queries.py"
echo -e ""
echo -e "   ${GREEN}# Run semantic case tests${NC}"
echo -e "   python scripts/test_semantic_cases.py"
echo -e ""
echo -e "   ${GREEN}# Start the FastAPI server${NC}"
echo -e "   uvicorn app.main:app --reload"

echo -e "\n${YELLOW}📝 Note: This script sets variables for the current shell session only.${NC}"
echo -e "${YELLOW}   For persistent configuration, create a .env file:${NC}"
echo -e "   cp env.template .env"
echo -e "   # Then edit .env with your actual values" 