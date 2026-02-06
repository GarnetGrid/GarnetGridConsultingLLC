# JGPT: Recommended Model Parameters

To ensure the highest quality responses for specialized tasks, JGPT uses the following recommended configurations for each persona.

## 📊 PowerBI Persona
Optimized for precision in DAX calculation and star-schema modeling.

| Parameter | Recommended Value | Rationale |
| :--- | :--- | :--- |
| **Model** | `llama3.2` | High reasoning capabilities for relational logic. |
| **Temperature** | `0.2` | Low temperature ensures deterministic and accurate DAX syntax. |
| **Context Window** | `8192` | Sufficient for most complex measure definitions and data model descriptions. |

## 🏗️ D365FO Persona
Optimized for X++ development, metadata awareness, and enterprise architectural standards.

| Parameter | Recommended Value | Rationale |
| :--- | :--- | :--- |
| **Model** | `codellama` | Specialized in coding tasks and boilerplate generation. |
| **Temperature** | `0.1` | Minimal variance for strict adherence to Chain of Command (CoC) patterns. |
| **Context Window** | `16384` | Larger window to handle multi-file extensions and large standard classes. |

## 🌐 Generic Assistant
Balanced for general reasoning and summaries.

| Parameter | Recommended Value | Rationale |
| :--- | :--- | :--- |
| **Model** | `llama3.2` (or similar) | Versatile and fast. |
| **Temperature** | `0.7` | Allows for creative and natural conversational flow. |
| **Context Window** | `4096` | Standard for most chat interactions. |

---
*Note: Users can override these defaults in the **Model Settings** popover in the Header.*
