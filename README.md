# Safe-Park

Cooperative Parking Authorization System

## Overview

Safe-Park is a cooperative intelligent transport system (C-ITS) designed to support parking authorization through coordinated communication between vehicles and roadside infrastructure. The system aims to determine whether parking is permitted at a given location based on predefined spatial rules and to inform the driver accordingly.

The project explores how infrastructure-assisted decision making can be applied to parking management, enabling consistent enforcement of parking regulations while reducing driver uncertainty.

## System Concept

The system is composed of three main entities:
	•	On-Board Unit (OBU), representing the vehicle logic and positioning capabilities.
	•	Road Side Unit (RSU), representing the infrastructure responsible for evaluating parking rules and enforcement conditions.
	•	Application Unit (AU), representing the interface through which the driver receives parking-related information.

Parking permissions are evaluated using a geofencing model, where specific spatial areas are associated with different parking policies. The RSU performs the authorization logic by matching the vehicle’s position against these predefined zones and communicating the resulting decision to the vehicle.

## Positioning and Spatial Model

Vehicle position is represented through coordinates obtained from a positioning mechanism, abstracted from the specific technology used to acquire them. This allows the system to remain independent of GPS or map providers while preserving the core geofencing logic.

Spatial areas are defined in advance and stored at the infrastructure level. Each area is associated with a parking policy, such as permitted or forbidden parking. This design enables straightforward scalability to real-world geographic data and urban environments.

## Enforcement Logic

When a vehicle requests parking authorization, the RSU evaluates whether the vehicle is located within a permitted area. If parking is not allowed, the system may initiate time-based enforcement mechanisms, allowing controlled tolerance periods before triggering further actions.

All user-facing information is communicated through the AU, ensuring a clear separation between decision logic and driver interaction.

## Objectives

	•	Implement cooperative parking authorization using vehicle–infrastructure communication.
	•	Apply geofencing principles to parking management.
	•	Separate infrastructure-based decision logic from vehicle user interfaces.
	•	Provide a scalable foundation for infrastructure-assisted parking enforcement.

## Conclusion

Safe-Park demonstrates how cooperative systems can be used to manage parking authorization in a structured and extensible manner. By combining spatial rule evaluation with vehicle–infrastructure communication, the system establishes a foundation for intelligent parking management that can be extended to larger and more complex urban environments.
