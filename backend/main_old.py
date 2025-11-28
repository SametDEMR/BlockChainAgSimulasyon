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
from backend.attacks.attack_engine import AttackEngine, AttackType
from backend.attacks.ddos import DDoSAttack
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
background_tasks_list = []

# Global attack engine instance
attack_engine = AttackEngine()


# Request Models
class StartRequest(BaseModel):
    """Start simulator request"""
    pass


class StopRequest(BaseModel):
    """Stop simulator request"""
    pass


class TriggerAttackRequest(BaseModel):
    """Trigger attack request"""
    attack_type: str
    target_node_id: str
    parameters: Optional[dict] = None


# Background task for auto block production
async def run_auto_production():
    """Background task that runs auto block production"""
    try:
        await simulator.auto_block_production()
    except asyncio.CancelledError:
        pass


# Background task for PBFT message processing
async def run_pbft_processing():
    """Background task that processes PBFT messages"""
    try:
        await simulator.pbft_message_processing()
    except asyncio.CancelledError:
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


@app.get("/network/nodes")
async def get_network_nodes():
    """Get detailed network nodes information including PBFT status"""
    nodes_info = []

    for node in simulator.nodes:
        node_info = node.get_status()

        # Add network specific info
        node_info['message_queue_size'] = simulator.message_broker.get_queue_size(node.id)

        nodes_info.append(node_info)

    return {
        "total_nodes": len(simulator.nodes),
        "validator_count": len(simulator.validator_nodes),
        "regular_count": len(simulator.regular_nodes),
        "nodes": nodes_info
    }


@app.get("/network/messages")
async def get_network_messages():
    """Get PBFT message traffic"""
    all_messages = simulator.message_broker.get_all_messages()
    pbft_messages = simulator.get_pbft_messages()

    # Mesaj tiplerini say
    message_types = {}
    for msg in pbft_messages:
        msg_type = msg.get('message_type', 'unknown')
        message_types[msg_type] = message_types.get(msg_type, 0) + 1

    return {
        "total_messages": len(all_messages),
        "pbft_messages": len(pbft_messages),
        "message_types": message_types,
        "broker_stats": simulator.message_broker.get_stats(),
        "recent_messages": pbft_messages[:20]  # Son 20 mesaj
    }


@app.get("/pbft/status")
async def get_pbft_status():
    """Get PBFT consensus status"""
    if not simulator.validator_nodes:
        return {
            "enabled": False,
            "message": "No validators in network"
        }

    # Primary validator bilgisi
    primary_node = None
    for validator in simulator.validator_nodes:
        if validator.pbft and validator.pbft.is_primary():
            primary_node = validator
            break

    # Tüm validator'ların stats'ı
    validator_stats = []
    for validator in simulator.validator_nodes:
        if validator.pbft:
            stats = validator.pbft.get_stats()
            validator_stats.append(stats)

    return {
        "enabled": True,
        "total_validators": len(simulator.validator_nodes),
        "primary": primary_node.id if primary_node else None,
        "current_view": validator_stats[0]['view'] if validator_stats else 0,
        "total_consensus_reached": sum(v['total_consensus_reached'] for v in validator_stats),
        "validators": validator_stats
    }


@app.post("/start")
async def start_simulator():
    """Start the simulator"""
    global background_tasks_list

    if simulator.is_running:
        return {
            "status": "warning",
            "message": "Simulator already running",
            "is_running": True
        }

    simulator.start()

    # Start background tasks
    production_task = asyncio.create_task(run_auto_production())
    pbft_task = asyncio.create_task(run_pbft_processing())

    background_tasks_list = [production_task, pbft_task]

    return {
        "status": "success",
        "message": "Simulator started with PBFT",
        "is_running": simulator.is_running,
        "background_tasks": 2
    }


@app.post("/stop")
async def stop_simulator():
    """Stop the simulator"""
    global background_tasks_list

    simulator.stop()

    # Cancel background tasks
    for task in background_tasks_list:
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    background_tasks_list = []

    return {
        "status": "success",
        "message": "Simulator stopped",
        "is_running": simulator.is_running
    }


@app.post("/reset")
async def reset_simulator():
    """Reset the simulator"""
    global background_tasks_list

    # Stop first if running
    if simulator.is_running:
        simulator.stop()
        for task in background_tasks_list:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        background_tasks_list = []

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
    print(f"PBFT: {'Enabled' if simulator.validator_nodes else 'Disabled'}")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global background_tasks_list

    simulator.stop()

    for task in background_tasks_list:
        if task and not task.done():
            task.cancel()
            try:
                await task
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
