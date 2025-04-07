#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PID file to track the bot process
PID_FILE=".bot.pid"

# Function to check if the bot is running
check_bot() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm "$PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

# Function to start the bot
start_bot() {
    if check_bot; then
        echo -e "${YELLOW}Bot is already running!${NC}"
        return
    fi
    
    echo -e "${GREEN}Starting telegram bot...${NC}"
    python main.py > bot.log 2>&1 &
    echo $! > "$PID_FILE"
    echo -e "${GREEN}Bot started successfully!${NC}"
    echo -e "Check bot.log for output"
}

# Function to stop the bot
stop_bot() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping bot...${NC}"
            kill "$pid"
            rm "$PID_FILE"
            echo -e "${GREEN}Bot stopped successfully!${NC}"
        else
            echo -e "${RED}Bot is not running!${NC}"
            rm "$PID_FILE"
        fi
    else
        echo -e "${RED}Bot is not running!${NC}"
    fi
}

# Function to show bot status
status_bot() {
    if check_bot; then
        echo -e "${GREEN}Bot is running${NC}"
        pid=$(cat "$PID_FILE")
        echo -e "Process ID: $pid"
    else
        echo -e "${RED}Bot is not running${NC}"
    fi
}

# Main script logic
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    status)
        status_bot
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 