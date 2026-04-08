---
name: s2-sssu-origin-alignment-brain
description: S2 Spatial Twin & Origin Alignment Brain. Enforces Z-axis reduction and mandatory 2D grid translation via the main entrance anchor, followed by tensor-based multimodal navigation.
version: 1.0.0
author: Space2.world (Miles Xiang)
tags: [Spatial-Twin, Grid-Alignment, Embodied-AI, SSSU, SP-OS]
allowed-tools: [s2_origin_alignment_execute]
metadata:
  clawdbot:
    requires:
      env: [S2_SWARM_PKI_ROOT]
---

# 🌐 S2-SSSU-Origin-Alignment-Brain: The Master Directives

Dear OpenClaw Agent,

You are entering a Lord-governed Smart Space (SSSU). Your internal SLAM coordinate system is initially misaligned with the physical building's digital twin. You must execute the alignment protocol before proceeding.

## Step 0: The Origin Anchoring (Mandatory)
Before requesting a Visa, you must identify the main entrance (入户门洞). The Lord defines the right vertex of the door bottom line as the absolute origin $(0,0)$ and the center as $(100,0)$.
Invoke `s2_origin_alignment_execute` with `action: ALIGN_SPATIAL_GRID`. Pass your SLAM's local coordinates for these two points. The Brain will return a 2D Transformation Matrix ($\Delta X, \Delta Y, \Delta \theta$). You must permanently snap your internal grid to this matrix.

## Step 1: Obtain a Visa
Invoke `action: REQUEST_VISA` to gain legal access to the aligned grids.

## Step 2: Tensor-based Navigation
Invoke `action: NAVIGATE_STEP`. Submit your continuous kinematics (Mass & Velocity) and multimodal sensor tensors. The Lord's backend handles dynamic object generation (TDOG) and momentum-based right-of-way yielding.