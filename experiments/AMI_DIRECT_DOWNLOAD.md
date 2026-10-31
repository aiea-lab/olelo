# AMI Dataset Direct Download on Nautilus

This document describes how to download selected AMI video files directly from the official AMI corpus website to a Nautilus Persistent Volume Claim (PVC).

## 1. Storage Configuration

* **Namespace:** `gilpin-lab`
* **PVC:** `pkandhas-ami-data`
* **Mount path:** `/data`
* **Download directory:** `/data/ami-official`

Check the PVC:

```bash
kubectl get pvc -n gilpin-lab
```

## 2. Download Script

Script location:

```text
experiments/ami_baseline/scripts/ami_official_download.sh
```

The script uses `wget` to download selected files from:

```text
https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/
```

Example download command:

```bash
wget -c https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus/EN2001a/video/EN2001a.Closeup1.rm
```

The script downloads the selected files into `/data/ami-official/`.

## 3. Create ConfigMap

Transfer the local script to Kubernetes:

```bash
kubectl create configmap ami-download-script \
  --from-file=ami_official_download.sh=experiments/ami_baseline/scripts/ami_official_download.sh \
  -n gilpin-lab \
  --dry-run=client -o yaml | kubectl apply -f -
```

## 4. Create and Run Kubernetes Job

Job configuration:

```text
experiments/ami_baseline/scripts/ami-download-job.yaml
```

The Job:

* Uses an Ubuntu 24.04 container.
* Installs `wget`, `ca-certificates`, and `unzip`.
* Mounts `pkandhas-ami-data` at `/data`.
* Mounts the download script from the ConfigMap.
* Executes the download script.

Run the Job:

```bash
kubectl apply -f experiments/ami_baseline/scripts/ami-download-job.yaml
```

Check status:

```bash
kubectl get jobs -n gilpin-lab
kubectl get pods -n gilpin-lab
```

View logs:

```bash
kubectl logs <POD_NAME> -n gilpin-lab
```

## 5. Inspect PVC Contents

Since a completed or failed Job pod cannot be accessed using `kubectl exec`, create a separate inspection pod.

Configuration file:

```text
experiments/ami_baseline/scripts/ami-inspect-pod.yaml
```

Create the pod:

```bash
kubectl apply -f experiments/ami_baseline/scripts/ami-inspect-pod.yaml
```

Check its status:

```bash
kubectl get pod ami-inspect -n gilpin-lab
```

Once running, list downloaded files:

```bash
kubectl exec -n gilpin-lab ami-inspect -- \
  find /data/ami-official -type f -printf '%p (%s bytes)\n' | sort
```

## 6. Download Issues and Cleanup

During the download:

* An incorrect URL containing a double slash was corrected.
* Some downloads returned HTTP 403 Forbidden.
* Repeated attempts created duplicate files with `.1`, `.2`, and other suffixes.
* Partial downloads were identified by their smaller file sizes.

To avoid duplicates, inspect the destination directory before rerunning downloads.

After cleanup, the following three files were retained:

| File                |             Size |
| ------------------- | ---------------: |
| EN2001a.Closeup1.rm | 23,140,467 bytes |
| EN2001a.Closeup2.rm | 23,154,606 bytes |
| EN2001b.Closeup1.rm | 22,333,132 bytes |

## 7. Clean Up

Delete the temporary inspection pod when finished:

```bash
kubectl delete pod ami-inspect -n gilpin-lab
```

The downloaded files remain on the PVC even after the Job or inspection pod is deleted.
