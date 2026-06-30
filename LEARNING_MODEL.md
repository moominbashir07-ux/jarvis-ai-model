# LEARNING_MODEL.md - Personalization Models & Heuristics

This document describes the underlying algorithms, feedback loop heuristics, and state probability score mappings used in JARVIS Personalization.

---

## 1. Adaptive Preference Weighting

The recommendation confidence score ($C_f$) is calculated by multiplying a base heuristic confidence score ($C_b$) by a preference modifier multiplier ($M_p$):

$$C_f = C_b \times M_p$$

Where $M_p$ is bounded:

$$0.1 \le M_p \le 2.0$$

The preference modifier $M_p$ shifts dynamically based on user selection outcomes:
* **Acceptance Feedback**: $M_p \leftarrow \min(2.0, M_p + 0.15)$
* **Rejection Feedback**: $M_p \leftarrow \max(0.1, M_p - 0.25)$
* **Ignore Timeout decay**: $M_p \leftarrow \max(0.2, M_p - 0.05)$

---

## 2. Heuristic Goal Prediction

Goal forecasting utilizes a transition sequence mapping (a simple Markov Chain state layout) based on application active transitions history:

| Current Active App | Next Predicted Action | Base Probability |
| :--- | :--- | :--- |
| `Code.exe` (VS Code) | Launch Terminal | `0.85` |
| `Code.exe` (VS Code) | Open Chrome for Docs | `0.65` |
| `Chrome.exe` | Resume Coding Session | `0.70` |
| `Chrome.exe` | Write Documentation | `0.50` |
| Others | Open VS Code | `0.60` |
