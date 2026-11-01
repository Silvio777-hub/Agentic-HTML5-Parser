# thesis/README.md — Thesis Chapter Outline

This folder documents the chapter structure of the MSc thesis:

> **"Trustworthy HTML5 Parser Development via Agentic AI: A Multi-Agent, Self-Healing Pipeline"**
>
> Author: Opoka JM Silvio | MSc Computer Science | 2026/2027

---

## Chapter Map

| Chapter | Title | Key Artifact |
|---|---|---|
| 1 | Introduction & Motivation | — |
| 2 | Background & Related Work | — |
| 3 | System Architecture | `ARCHITECTURE.md` |
| 4 | Implementation | `src/`, `orchestrator.py` |
| 5 | Evaluation & Results | `data/*.json`, `figures/*.png` |
| 6 | Discussion & Limitations | — |
| 7 | Conclusion & Future Work | — |

---

## Chapter 5 — Key Evaluation Data

All results are reproducible by running:

```bash
python cli.py test          # → 139/139 unit tests
python cli.py compliance    # → compliance_results.json
python cli.py adversarial   # → adversarial_results.json
python cli.py benchmark     # → benchmark_results.json
python cli.py ablation      # → ablation_study_results.json
python cli.py charts        # → figures/*.png
```
