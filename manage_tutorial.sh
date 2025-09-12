#!/bin/bash

# Epydemics Tutorial Management Script
# This script helps manage the epydemics-tutorial submodule easily

set -e

SUBMODULE_PATH="epydemics-tutorial"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "This directory is not a git repository!"
        exit 1
    fi
}

# Function to initialize submodule
init_submodule() {
    print_header "Initializing submodule..."
    
    if [ -d "$SUBMODULE_PATH" ] && [ "$(ls -A $SUBMODULE_PATH)" ]; then
        print_status "Submodule already initialized and populated"
    else
        print_status "Initializing and updating submodule..."
        git submodule update --init --recursive
        print_status "Submodule initialized successfully!"
    fi
}

# Function to update submodule to latest
update_submodule() {
    print_header "Updating submodule to latest version..."
    
    if [ ! -d "$SUBMODULE_PATH" ]; then
        print_error "Submodule not found. Run 'init' first."
        exit 1
    fi
    
    print_status "Fetching latest changes..."
    git submodule update --remote --merge "$SUBMODULE_PATH"
    
    # Check if there are changes to commit
    if git diff --quiet HEAD -- .gitmodules "$SUBMODULE_PATH"; then
        print_status "Submodule is already up to date"
    else
        print_warning "Submodule has been updated. Consider committing the changes:"
        echo "  git add .gitmodules $SUBMODULE_PATH"
        echo "  git commit -m \"Update tutorial submodule to latest version\""
    fi
}

# Function to check submodule status
status_submodule() {
    print_header "Checking submodule status..."
    
    if [ ! -d "$SUBMODULE_PATH" ]; then
        print_warning "Submodule directory not found"
        return
    fi
    
    # Check if submodule is initialized
    if [ ! -f "$SUBMODULE_PATH/.git" ] && [ ! -d "$SUBMODULE_PATH/.git" ]; then
        print_warning "Submodule not initialized"
        return
    fi
    
    print_status "Submodule status:"
    git submodule status "$SUBMODULE_PATH"
    
    # Check for uncommitted changes in main repo
    if ! git diff --quiet HEAD -- .gitmodules "$SUBMODULE_PATH"; then
        print_warning "There are uncommitted changes related to the submodule"
    fi
    
    # Check submodule's local status
    cd "$SUBMODULE_PATH"
    if ! git diff --quiet; then
        print_warning "Submodule has uncommitted changes"
    fi
    cd - > /dev/null
}

# Function to reset submodule
reset_submodule() {
    print_header "Resetting submodule..."
    
    if [ ! -d "$SUBMODULE_PATH" ]; then
        print_error "Submodule not found"
        exit 1
    fi
    
    print_warning "This will reset the submodule to the committed state and lose any local changes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$SUBMODULE_PATH"
        git reset --hard HEAD
        git clean -fd
        cd - > /dev/null
        git submodule update --init --recursive
        print_status "Submodule reset successfully"
    else
        print_status "Reset cancelled"
    fi
}

# Function to open tutorial in default application
open_tutorial() {
    print_header "Opening tutorial..."
    
    if [ ! -d "$SUBMODULE_PATH" ]; then
        print_error "Submodule not found. Run 'init' first."
        exit 1
    fi
    
    # Look for common tutorial files
    TUTORIAL_FILES=(
        "$SUBMODULE_PATH/README.md"
        "$SUBMODULE_PATH/tutorial.ipynb"
        "$SUBMODULE_PATH/index.html"
        "$SUBMODULE_PATH"
    )
    
    for file in "${TUTORIAL_FILES[@]}"; do
        if [ -e "$file" ]; then
            print_status "Opening $file..."
            if command -v code > /dev/null; then
                code "$file"
            elif command -v xdg-open > /dev/null; then
                xdg-open "$file"
            elif command -v open > /dev/null; then
                open "$file"
            else
                print_status "Please open $file manually"
            fi
            return
        fi
    done
    
    print_warning "No tutorial files found. Opening submodule directory..."
    if command -v code > /dev/null; then
        code "$SUBMODULE_PATH"
    else
        print_status "Please navigate to $SUBMODULE_PATH manually"
    fi
}

# Function to show help
show_help() {
    cat << EOF
Epydemics Tutorial Management Script

USAGE:
    $0 <command>

COMMANDS:
    init        Initialize the tutorial submodule
    update      Update submodule to latest version
    status      Check submodule status
    reset       Reset submodule to clean state (loses local changes!)
    open        Open tutorial in default application
    help        Show this help message

EXAMPLES:
    $0 init     # Initialize submodule for first use
    $0 update   # Get latest tutorial content
    $0 status   # Check current state
    $0 open     # Open tutorial files

EOF
}

# Main script logic
main() {
    cd "$SCRIPT_DIR"
    check_git_repo
    
    case "${1:-help}" in
        "init")
            init_submodule
            ;;
        "update")
            update_submodule
            ;;
        "status")
            status_submodule
            ;;
        "reset")
            reset_submodule
            ;;
        "open")
            open_tutorial
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"