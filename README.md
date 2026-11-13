# Simulation-of-Autonomous-Road-Merging

## AFEKA - Tel-Aviv Academic College Of Engineering<br/>Department: Intelligent Systems<br/>Course: Autonomous Vehicle

---

**Course project:** Development of an autonomous road merging simulation with adaptive learning behavior.  
The simulation models autonomous vehicle merging from a secondary road into a main traffic road.

**Development Tools:** Python, Pygame  

**Main Concepts:**  
Adaptive security area, autonomous merging logic, collision detection, state-machine based control, dynamic traffic simulation.

---

## Overview

The project was inspired by:
- adaptive cruise control systems,
- slot-based merging approaches,
- autonomous driving decision-making algorithms.

The simulation models:
- traffic vehicles with dynamic speeds,
- autonomous merging behavior,
- collision detection,
- adaptive security areas,
- environment state transitions,
- basic learning behavior based on previous collisions.

The ego vehicle performs merging using a finite-state logic:
- Start
- Slow Down
- Wait
- Turn
- Speed Up
- Regular Speed

The adaptive learning mechanism updates the security area near the merge point according to:
- collision direction,
- traffic speed,
- previous failures.

If collisions continue to occur, the security area increases dynamically in order to create safer merging behavior.

---

## Core Idea

The project is inspired by slot-based autonomous merging approaches such as iPCB and GeoACC.

The main idea is to create a dynamic security area near the merge point and allow the ego vehicle to enter the main road only when the area is considered safe.

The security area adapts according to:
- previous collisions,
- traffic speed,
- collision direction,
- environment behavior over time.

This creates a simple adaptive learning mechanism that improves merging behavior after failures.

![Core Idea](image/core_idea.png)

---

## Simulation Screenshot

![Simulation Screenshot](image/screenshot.png)

The simulation window displays:
- traffic vehicles on the main road,
- the ego vehicle entering from the secondary road,
- adaptive security area parameters,
- vehicle speed,
- steering angle,
- acceleration,
- statistics of successful and failed merging attempts.

---

## Results

To measure the effect of the adaptive security area, the simulation was run without the window
(see `experiments/`) for 2,000 episodes, 5 times with different random traffic.
For comparison, the same runs were made with learning disabled: the security area is not updated
after a crash, so the ego vehicle merges without checking the traffic.

![Crash rate during learning](image/crash_rate.png)

| | Without learning | With adaptive security area |
|---|---:|---:|
| Crashes, episodes 1–50 | 47% | 14% |
| Crashes, episodes 101–500 | 44% | 3.3% |
| Crashes, episodes 1001–2000 | 45% | 6.0% |
| Average episode duration | 5.6 s | 7.8 s |

- **The security area learns fast:** the crash rate falls from about 47% to a few percent
  within the first 100 episodes.
- **It does not go to zero by design:** after a crash the security area grows, and after every
  10 episodes without crashes it shrinks a little (to reduce waiting). These two rules balance
  at about 5–6% crashes – a trade-off between safety and waiting time.
- **The price of safety is waiting:** the ego vehicle waits more often before the merge point,
  so an episode lasts 7.8 s instead of 5.6 s.

---

## Main Features

- Autonomous merge decision making
- Dynamic traffic generation
- Collision detection
- Adaptive security area learning
- State-machine based vehicle control
- Traffic speed adaptation
- Visual simulation using Pygame

---

## Code Structure

### PlayerCar
- ResetPlayerCar
- CrashProcess
- Update

### Environment
- Get_start_slowdown_point
- Get_dist_till_merge
- Update
- If_allow_turn
- Update_coll_shifts
- Step

---

## Running the Project

Install dependencies:

```bash
pip install pygame
```

Run the simulation:

```bash
python roads_merge_simulation.py
```

Reproduce the results (no window; pygame drawing is replaced by a stub, the simulation logic runs unchanged):

```bash
python experiments/run_headless.py roads_merge_simulation.py results/run_s1_L1.csv 2000 1 1
python experiments/run_headless.py roads_merge_simulation.py results/run_s1_L0.csv 2000 1 0
python experiments/plot_crash_rate.py results image/crash_rate.svg
```

Each run writes one CSV row per episode (crash flag, duration in frames, security area values).
The last argument of `run_headless.py` turns learning on (1) or off (0); the chart above uses seeds 1–5.

---

## Notes

This project was developed as part of a group academic project.

The implementation and programming were primarily written by me.
