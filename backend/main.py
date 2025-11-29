"""
FastAPI Backend - Main API Server with Attack Endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulator import Simulator
from backend.attacks.attack_engine import AttackEngine, AttackType
from backend.attacks.ddos import DDoSAttack
from backend.attacks.byzantine import ByzantineAttack
from backend.attacks.sybil import SybilAttack
from config import get_api_config

app = FastAPI(
    title="Blockchain Attack Simulator API",
    description="Interactive Blockchain Network Simulator with Attack Scenarios",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = Simulator()
attack_engine = AttackEngine()
byzantine_attack = ByzantineAttack(simulator)
sybil_attack = SybilAttack(simulator)
background_tasks_list = []


class TriggerAttackRequest(BaseModel):
    attack_type: str
    target_node_id: str
    parameters: Optional[dict] = None


async def run_auto_production():
    try:
        await simulator.auto_block_production()
    except asyncio.CancelledError:
        pass


async def run_pbft_processing():
    try:
        await simulator.pbft_message_processing()
    except asyncio.CancelledError:
        pass


@app.get("/")
async def root():
    return {"status": "ok", "message": "Blockchain Attack Simulator API", "version": "1.0.0"}


@app.get("/status")
async def get_status():
    return simulator.get_status()


@app.get("/blockchain")
async def get_blockchain():
    if not simulator.nodes:
        raise HTTPException(status_code=404, detail="No nodes available")
    node = simulator.nodes[0]
    return {"chain_length": len(node.blockchain.chain), "chain": node.blockchain.to_dict()}


@app.get("/nodes")
async def get_nodes():
    return {"total_nodes": len(simulator.nodes), "nodes": simulator.get_all_nodes_status()}


@app.get("/nodes/{node_id}")
async def get_node(node_id: str):
    node = simulator.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node.get_status()


@app.get("/network/nodes")
async def get_network_nodes():
    nodes_info = []
    for node in simulator.nodes:
        node_info = node.get_status()
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
    all_messages = simulator.message_broker.get_all_messages()
    pbft_messages = simulator.get_pbft_messages()
    message_types = {}
    for msg in pbft_messages:
        msg_type = msg.get('message_type', 'unknown')
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    return {
        "total_messages": len(all_messages),
        "pbft_messages": len(pbft_messages),
        "message_types": message_types,
        "broker_stats": simulator.message_broker.get_stats(),
        "recent_messages": pbft_messages[:20]
    }


@app.get("/pbft/status")
async def get_pbft_status():
    if not simulator.validator_nodes:
        return {"enabled": False, "message": "No validators in network"}
    
    primary_node = None
    for validator in simulator.validator_nodes:
        if validator.pbft and validator.pbft.is_primary():
            primary_node = validator
            break
    
    validator_stats = []
    for validator in simulator.validator_nodes:
        if validator.pbft:
            validator_stats.append(validator.pbft.get_stats())
    
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
    global background_tasks_list
    
    if simulator.is_running:
        return {"status": "warning", "message": "Simulator already running", "is_running": True}
    
    simulator.start()
    production_task = asyncio.create_task(run_auto_production())
    pbft_task = asyncio.create_task(run_pbft_processing())
    background_tasks_list = [production_task, pbft_task]
    
    return {"status": "success", "message": "Simulator started", "is_running": True, "background_tasks": 2}


@app.post("/stop")
async def stop_simulator():
    global background_tasks_list
    simulator.stop()
    for task in background_tasks_list:
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    background_tasks_list = []
    return {"status": "success", "message": "Simulator stopped", "is_running": False}


@app.post("/reset")
async def reset_simulator():
    global background_tasks_list
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
    attack_engine.reset()
    return {"status": "success", "message": "Reset complete", "total_nodes": len(simulator.nodes)}


# Attack Endpoints
@app.post("/attack/trigger")
async def trigger_attack(request: TriggerAttackRequest):
    target_node = simulator.get_node_by_id(request.target_node_id)
    if not target_node:
        raise HTTPException(status_code=404, detail="Target node not found")
    
    try:
        attack_type = AttackType(request.attack_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid attack type: {request.attack_type}")
    
    if attack_type == AttackType.DDOS:
        intensity = request.parameters.get("intensity", "high") if request.parameters else "high"
        ddos = DDoSAttack(target_node=target_node, attack_engine=attack_engine, intensity=intensity)
        attack_id = await ddos.execute()
        
        return {
            "status": "success",
            "message": f"DDoS attack triggered on {request.target_node_id}",
            "attack_id": attack_id,
            "attack_type": attack_type.value,
            "target": request.target_node_id,
            "parameters": {"intensity": intensity}
        }
    
    elif attack_type == AttackType.BYZANTINE:
        result = byzantine_attack.trigger(request.target_node_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "status": "success",
            "message": result["message"],
            "attack_type": attack_type.value,
            "target": request.target_node_id,
            "duration": result.get("duration", 30)
        }
    
    else:
        raise HTTPException(status_code=501, detail=f"Attack {attack_type.value} not implemented")


@app.get("/attack/status")
async def get_attack_status():
    return {
        "active_attacks": attack_engine.get_active_attacks(),
        "recent_history": attack_engine.get_attack_history(limit=10),
        "statistics": attack_engine.get_statistics()
    }


@app.get("/attack/status/{attack_id}")
async def get_specific_attack_status(attack_id: str):
    attack = attack_engine.get_attack_status(attack_id)
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    return attack


@app.post("/attack/stop/{attack_id}")
async def stop_attack_endpoint(attack_id: str):
    success = attack_engine.stop_attack(attack_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attack not found or already stopped")
    return {"status": "success", "message": f"Attack {attack_id} stopped", "attack_id": attack_id}


@app.get("/attack/byzantine/status")
async def get_byzantine_attack_status():
    """Byzantine saldırı durumunu döndür"""
    return byzantine_attack.get_status()


@app.post("/attack/byzantine/stop")
async def stop_byzantine_attack():
    """Byzantine saldırısını durdur"""
    result = byzantine_attack.stop()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/attack/sybil/trigger")
async def trigger_sybil_attack(num_nodes: int = 20):
    """Sybil saldırısını tetikle"""
    success = await sybil_attack.trigger(num_nodes=num_nodes)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to trigger Sybil attack")
    return {
        "status": "success",
        "message": f"Sybil attack triggered with {num_nodes} fake nodes",
        "attack_id": sybil_attack.attack_id,
        "attack_status": sybil_attack.get_status()
    }


@app.get("/attack/sybil/status")
async def get_sybil_attack_status():
    """Sybil saldırı durumunu döndür"""
    return sybil_attack.get_status()


@app.post("/attack/sybil/stop")
async def stop_sybil_attack():
    """Sybil saldırısını durdur"""
    success = await sybil_attack.stop()
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop Sybil attack")
    return {
        "status": "success",
        "message": "Sybil attack stopped",
        "attack_status": sybil_attack.get_status()
    }


@app.get("/metrics")
async def get_all_metrics():
    return {
        "total_nodes": len(simulator.nodes),
        "metrics": [
            {
                "node_id": node.id,
                "role": node.role,
                "status": node.status,
                "metrics": node.get_metrics()
            }
            for node in simulator.nodes
        ]
    }


@app.get("/metrics/{node_id}")
async def get_node_metrics(node_id: str):
    node = simulator.get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"node_id": node.id, "role": node.role, "status": node.status, "metrics": node.get_metrics()}


@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🚀 Blockchain Attack Simulator API")
    print(f"Nodes: {len(simulator.nodes)} | Validators: {len(simulator.validator_nodes)}")
    print("Attack Engine: Ready")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    global background_tasks_list
    simulator.stop()
    for task in background_tasks_list:
        if task and not task.done():
            task.cancel()
    print("Shutdown complete")


if __name__ == "__main__":
    config = get_api_config()
    uvicorn.run("main:app", host=config['host'], port=config['port'], reload=config['reload'])
