#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LAUNCH_AGENT_NAME="com.user.telegrambot"
LAUNCH_AGENT_FILE="$LAUNCH_AGENT_NAME.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

# Function to check if the Launch Agent is loaded
is_loaded() {
    launchctl list | grep -q "$LAUNCH_AGENT_NAME"
    return $?
}

# Function to load the Launch Agent
load_agent() {
    if is_loaded; then
        echo -e "${YELLOW}Launch Agent is already loaded!${NC}"
        return
    fi
    
    echo -e "${GREEN}Loading Launch Agent...${NC}"
    launchctl load "$LAUNCH_AGENTS_DIR/$LAUNCH_AGENT_FILE"
    echo -e "${GREEN}Launch Agent loaded successfully!${NC}"
}

# Function to unload the Launch Agent
unload_agent() {
    if ! is_loaded; then
        echo -e "${RED}Launch Agent is not loaded!${NC}"
        return
    fi
    
    echo -e "${YELLOW}Unloading Launch Agent...${NC}"
    launchctl unload "$LAUNCH_AGENTS_DIR/$LAUNCH_AGENT_FILE"
    echo -e "${GREEN}Launch Agent unloaded successfully!${NC}"
}

# Function to install the Launch Agent
install_agent() {
    echo -e "${GREEN}Installing Launch Agent...${NC}"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # Copy the plist file
    cp "$LAUNCH_AGENT_FILE" "$LAUNCH_AGENTS_DIR/"
    
    # Set correct permissions
    chmod 644 "$LAUNCH_AGENTS_DIR/$LAUNCH_AGENT_FILE"
    
    echo -e "${GREEN}Launch Agent installed successfully!${NC}"
}

# Function to show status
show_status() {
    if is_loaded; then
        echo -e "${GREEN}Launch Agent is loaded and running${NC}"
    else
        echo -e "${RED}Launch Agent is not loaded${NC}"
    fi
}

# Main script logic
case "$1" in
    install)
        install_agent
        ;;
    start)
        load_agent
        ;;
    stop)
        unload_agent
        ;;
    restart)
        unload_agent
        sleep 2
        load_agent
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {install|start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 