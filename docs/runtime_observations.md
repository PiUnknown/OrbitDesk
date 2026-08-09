# Runtime Observations

These are local cache and demonstration observations for the submission. Re-run the CLI on the final machine and replace any hardware placeholders with exact values.

## Cached model revisions

- `BAAI/bge-small-en-v1.5`: `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`
- `Qwen/Qwen2.5-0.5B-Instruct`: `7ae557604adf67be50417f59c2c2f167def9a775`
- `Qwen/Qwen2.5-3B-Instruct`: `aa8e72537993ba99e69dfaafa59ed015b17504d1`

The default live generator is the 0.5B model because the 3B model was disk-offloaded and was impractical on the available CPU-only machine.

## Observed live runs

- Direct API-credential question: approximately 31.56 seconds.
- Timezone/export multi-document question: approximately 64.30 seconds.
- Both runs showed `model_mode=transformers`, citation pass, grounding pass, schema pass, and no final retry.

## Hardware record

Captured from Windows Task Manager on the demonstration machine:

- CPU: Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz (4 cores, 8 logical processors)
- RAM: 16.0 GB DDR4 (15.8 GB usable)
- GPU/accelerator: NVIDIA GeForce GTX 1650, 4.0 GB dedicated GPU memory; Intel(R) UHD Graphics also present
- Storage: Micron 2210 NVMe SSD, 477 GB
- OS/interface: Windows with PowerShell

The CLI now prints `Model info` containing embedding/generation model names, revisions, load timings, and generation mode. Copy that block into the final submission notes. The GTX 1650 was idle during the observed run; generation was effectively CPU/disk-offloaded, which explains the high latency.
