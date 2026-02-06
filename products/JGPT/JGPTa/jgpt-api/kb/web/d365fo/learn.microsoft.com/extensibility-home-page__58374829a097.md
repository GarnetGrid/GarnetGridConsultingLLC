# Extensibility home page

**Source:** https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensibility-home-page
**Captured:** 2026-02-02
**Domain:** d365fo

Partners, value added resellers (VARs), and even some customers extensively customize Dynamics 365 Finance, Supply Chain, and Commerce. The ability to customize the product is a strength that historically was supported through overlayering of the application code. The move to the cloud, together with more agile servicing and frequent updates, requires a less intrusive customization model, so that updates are less likely to affect custom solutions. This new model is called *extensibility* and it replaces customization through overlayering.

Extensibility is the only customization framework in Finance, Supply Chain, and Commerce. Overlayering isn't supported.

## Introduction

These introductory topics contain general information about customization. This information includes details about when the transition occurs from customization through overlayering to a purely extension-based model. These topics also explain how to log extensibility requests to Microsoft, and provide answers to frequently asked questions (FAQ).

## What's new

For extensibility-related updates that have been made since July 2017, see [What's new or changed for extensibility](extensibility-new).

## Getting started

The topics in this section help you start to build extensions. They also help you migrate solutions that are currently based on overlayered code to extension-based solutions. This section includes hands-on labs that walk you through simple customizations.

## Fundamentals on extensions

This section includes fundamentals, principles, and practices for making extensions. The guiding principles in these topics discuss how to approach customization through extensions. These principles include naming guidelines. Additionally, these topics discuss the foundation framework, such as extensions and chain of command.

## How do I create extensions?

This section includes "How do I?" topics that explain how to customize specific object types or code. Most of these topics are brief and to the point. Because there are many topics here, it might be practical to search for a specific article.

### Data types

### Classes

### Tables

### Forms

### Others

### Reports

### Blog posts

Developers share information about customization through blogs where they discuss various topics. This section includes references to some of these blogs.

## How do I create an extensible solution?

This section includes some best practices on how to create an extensible solution, so that consumers of your code can extend your solution.

## Breaking changes

When you make your solution extensible, you also help guarantee that you don't break those extension points later.

* For pointers that can help you avoid breaking your consumers, see [Breaking changes](breaking-changes).
* The [compatibility checker tool](compatibility-checker-tool) can detect metadata breaking changes against a given baseline release or update, helping to ensure backward compatibility.
