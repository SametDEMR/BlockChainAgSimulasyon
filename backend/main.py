"""
FastAPI Backend - Main API Server
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulator import Simulator
from config import get_api_config

# FastAPI app
app = FastAPI(
    title="Blockchain Attack Simulator API",
    description="Interactive Blockchain Network Simulator with Attack Scenarios",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulator instance
simulator = Simulator()


# Request Models
class StartRequest(BaseModel):
    """Start simulator request"""
    pass


class StopRequest(BaseModel):
    """Stop simulator request"""
    pass


# Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Blockchain Attack Simulator API",
        "version": "1.0.0"
    }


@app.get("/status")
async def get_status():
    """Get simulator status"""
    return simulator.get_status()


@app.get("/blockchain")
async def get_blockchain():
    """Get full blockchain from first node"""
    if not simulator.nodes:
        raise HTTPException(status_code=404, detail="No nodes available")
    
    node = simulator.nodes[0]
    return {
        "chain_length": len(node.blockchain.chain),
        "chain": node.blockchain.to_dict()
    }


@app.get("/nodes")
async def get_nodes():
    """Get all nodes status"""
    return {
        "total_nodes": len(simulator.nodes),
        "nodes": simulator.get_all_nodes_status()
    }


@app.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Get specific node status"""
    node = simulator.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return node.get_status()


@app.post("/start")
async def start_simulator():
    """Start the simulator"""
    simulator.start()
    return {
        "status": "success",
        "message": "Simulator started",
        "is_running": simulator.is_running
    }


@app.post("/stop")
async def stop_simulator():
    """Stop the simulator"""
    simulator.stop()
    return {
        "status": "success",
        "message": "Simulator stopped",
        "is_running": simulator.is_running
    }


@app.post("/reset")
async def reset_simulator():
    """Reset the simulator"""
    simulator.reset()
    return {
        "status": "success",
        "message": "Simulator reset",
        "total_nodes": len(simulator.nodes)
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 60)
    print("🚀 Blockchain Attack Simulator API Starting...")
    print("=" * 60)
    print(f"Nodes: {len(simulator.nodes)}")
    print(f"Validators: {len(simulator.validator_nodes)}")
    print(f"Regular: {len(simulator.regular_nodes)}")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    simulator.stop()
    print("API Server shutdown")


# Run server
if __name__ == "__main__":
    config = get_api_config()
    
    uvicorn.run(
        "main:app",
        host=config['host'],
        port=config['port'],
        reload=config['reload']
    )
