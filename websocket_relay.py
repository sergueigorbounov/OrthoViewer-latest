#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket_relay")

# Store connected clients
frontend_clients = set()

async def message_relay(websocket, path):
    """Handle WebSocket connections and relay messages between services"""
    client_type = None
    try:
        # Initial handshake to identify the client
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Register client type on first message
                if not client_type and "client_type" in data:
                    client_type = data["client_type"]
                    if client_type == "frontend":
                        frontend_clients.add(websocket)
                        logger.info(f"Frontend client connected. Total: {len(frontend_clients)}")
                    
                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "type": "connection_ack",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Connected as {client_type} client"
                    }))
                    continue
                
                # Broadcast option for messages that should go to all clients
                if "target" in data and data["target"] == "broadcast":
                    if frontend_clients:
                        await asyncio.gather(
                            *[client.send(message) for client in frontend_clients 
                              if client != websocket]  # Don't send back to sender
                        )
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {message[:100]}...")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Clean up on disconnect
        if client_type == "frontend" and websocket in frontend_clients:
            frontend_clients.remove(websocket)
            logger.info(f"Frontend client disconnected. Remaining: {len(frontend_clients)}")

async def main():
    # Get port from command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8004
    logger.info(f"Starting WebSocket relay server on port {port}")
    async with websockets.serve(message_relay, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
