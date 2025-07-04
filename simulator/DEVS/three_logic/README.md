<h1 align="center">🚦 DEVS Traffic Model 📡</h1>

<p align="center">
  <a href="https://en.wikipedia.org/wiki/Discrete_Event_system_Specification">
    <img src="https://img.shields.io/badge/Model-DEVS-blue" alt="DEVS Model" />
  </a>
  <a href="#formalism-of-atomic-devs">
    <img src="https://img.shields.io/badge/Formalism-Specification-brightgreen" alt="Formalism" />
  </a>
  <a href="#traffic-model">
    <img src="https://img.shields.io/badge/Application-Traffic_Model-orange" alt="Traffic Model" />
  </a>
</p>

<p align="center">
  <strong>Modular DEVS-based traffic simulation model</strong><br>
  This project models a road network using <a href="https://en.wikipedia.org/wiki/Discrete_Event_system_Specification">Discrete Event System Specification (DEVS)</a>, enabling decentralized traffic coordination via formal simulation logic.
</p>

---

**Author**: Belén López Salamanca

**Date**: 04-07-2025
 
**Version**: 1.0.0

---

## 📚 Table of Contents
- [🔍 DEVS](#devs)
- [📐 Formalism of Atomic DEVS](#formalism-of-atomic-devs)
- [🛣️ Traffic Model](#traffic-model)
- [📊 Property Definition](#property-definition)
- [🧩 Modeling](#modeling)
  - [🧠 Initial Ideas](#initial-ideas)
  - [⚙️ DEVS 1](#devs-1)
  - [🔄 DEVS 2](#devs-2)
  - [📥 DEVS 3](#devs-3)

---

## 🔍 DEVS
**Discrete Event System Specification (DEVS)** is a formalism for modeling and analyzing general systems that can be described by events over time. This project references the atomic DEVS model to simulate traffic behavior modularly.

---

## 📐 Formalism of Atomic DEVS

The atomic DEVS model is defined as a 7-tuple:

**M = ⟨X, Y, S, s₀, ta, δext, δint, λ⟩**

- **X** → Input events  
- **Y** → Output events  
- **S** → Set of sequential states  
- **s₀ ∈ S** → Initial state  
- **ta: S → T⁺** → Time advance function (state lifespan)  
- **δext: Q × X → S** → External transition function  
  - Defines how input events change the state  
  - Q = { (s, te) | s ∈ S, te ∈ (ℝ⁺ ∩ [0, ta(s)]) }, te: elapsed time since last event  
- **δint: S → S** → Internal transition function  
  - Defines how a state changes internally when its lifetime ends  
- **λ: S → Y^Φ** → Output function  
  - Defines how a state produces output events

---

## 🛣️ Traffic Model

The system aims to simulate a modular traffic network where each road segment is autonomous yet capable of coordinating with neighboring segments through events, allowing vehicles to move road-to-road based on calculated timing.

---

## 📊 Property Definition

Road segments are ideally divided by intersections, traffic lights, or bifurcations. Each segment includes:

**Static properties:**
- Maximum speed  
- Street length  
- From these, maximum occupancy and minimum travel time are derived  

**Dynamic properties:**
- Fixed-size circular queue to track vehicle positions and speeds  
- Head and tail pointers for managing the queue  

**Timing variables:**
- `global_t`: Current global time of the road  
- `max_global_t`: Time needed for the first vehicle to reach the end  
- `prev_global_t`: Previous global time used to compute distance moved  

**Buffer structures** are included to comply with DEVS formalism.

---

## 🧩 Modeling

### 🧠 Initial Ideas

To coordinate roads, each road *i* requires:
- From road *i-1*: When a car will be at the end → used to synchronize motion  
- From road *i+1*: Global time and status (whether it can receive a car)  
- This enables sending a vehicle forward if timing and conditions allow  

Because DEVS limits to one input/output per transition, the traffic system is structured into three sequential DEVS modules.

---

### ⚙️ DEVS 1

**Responsible for car movement within a road segment.**

- **Step 3:** Sends `max_global_t` and `global_t` to the next road.
- **Step 5:** Processes input from previous road and updates `global_t`  
- **Step 6:** Moves cars in the road (no jumping among roads as that will be consider another input/output) accordingly and updates `prev_global_t`

---

### 🔄 DEVS 2

**Determines whether a vehicle can be sent to the next road.**

- **Step 3:** Sends `global_t`, `nof_vehicles`, `poistion of the last car in the road` of the road to the next one
- **Steps 5–6:** Evaluates if first vehicle in the queue meets the transition conditions  
  - If yes, sets `send_car = True`

---

### 📥 DEVS 3

**Handles sending and receiving vehicles between roads.**

- If `send_car` is possible, the car is send. Combines all steps for simplicity  
- Also contains logic to insert and remove vehicles from the system

---
