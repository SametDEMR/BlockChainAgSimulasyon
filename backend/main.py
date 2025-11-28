"""
FastAPI Backend - Main API Server
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os
import asyncio

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
background_task = None


# Request Models
class StartRequest(BaseModel):
    """Start simulator request"""
    pass


class StopRequest(BaseModel):
    """Stop simulator request"""
    pass


# Background task for auto block production
async def run_auto_production():
    """Background task that runs auto block production"""
    await simulator.auto_block_production()


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
async def start_simulator(background_tasks: BackgroundTasks):
    """Start the simulator"""
    global background_task
    
    if simulator.is_running:
        return {
            "status": "warning",
            "message": "Simulator already running",
            "is_running": True
        }
    
    simulator.start()
    
    # Start background task
    background_task = asyncio.create_task(run_auto_production())
    
    return {
        "status": "success",
        "message": "Simulator started",
        "is_running": simulator.is_running
    }


@app.post("/stop")
async def stop_simulator():
    """Stop the simulator"""
    global background_task
    
    simulator.stop()
    
    # Cancel background task
    if background_task and not background_task.done():
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    
    return {
        "status": "success",
        "message": "Simulator stopped",
        "is_running": simulator.is_running
    }


@app.post("/reset")
async def reset_simulator():
    """Reset the simulator"""
    global background_task
    
    # Stop first if running
    if simulator.is_running:
        simulator.stop()
        if background_task and not background_task.done():
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                pass
    
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
    global background_task
    
    simulator.stop()
    
    if background_task and not background_task.done():
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    
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
