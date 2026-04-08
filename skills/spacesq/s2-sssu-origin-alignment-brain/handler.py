#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
from core.visa_manager import SpatioTemporalVisaManager
from core.spatial_ledger import SpatialLedger
from core.lord_brain import LordGovernanceBrain
from core.robot_navigation_pipeline import S2RobotNavigationPipeline
from core.grid_alignment_engine import S2GridAlignmentEngine

class S2OriginAlignmentBrain:
    def __init__(self):
        self.visa_mgr = SpatioTemporalVisaManager()
        self.ledger = SpatialLedger()
        self.lord = LordGovernanceBrain(self.visa_mgr, self.ledger)
        self.alignment_engine = S2GridAlignmentEngine()

    def process_tool_call(self, args: dict) -> str:
        try:
            action = args.get("action")
            
            # [新增] 第0步：强制空间原点对齐
            if action == "ALIGN_SPATIAL_GRID":
                res = self.alignment_engine.execute_alignment(
                    args.get("robot_id"), 
                    args.get("local_door_origin", {"x": 0, "y": 0}), 
                    args.get("local_door_center", {"x": 100, "y": 0})
                )
            
            elif action == "REQUEST_VISA":
                res = self.visa_mgr.issue_visa(args.get("robot_id"), args.get("task"), args.get("requested_grids", []))
            elif action == "NAVIGATE_STEP":
                pipeline = S2RobotNavigationPipeline(args.get("robot_id"), args.get("visa_token"), self.lord)
                res = pipeline.execute_step(args.get("target_hex"), args.get("sensors"), args.get("kinematics", {"mass_kg": 20, "velocity_m_s": 0}), args.get("peer_state"))
            else:
                res = {"status": "error", "message": "Unknown action."}
            
            return json.dumps({"status": "success", "data": res}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    brain = S2OriginAlignmentBrain()
    if len(sys.argv) > 1:
        print(brain.process_tool_call(json.loads(sys.argv[1])))
    else:
        print(json.dumps({"status": "ready", "message": "S2 Origin Alignment Brain Online"}))