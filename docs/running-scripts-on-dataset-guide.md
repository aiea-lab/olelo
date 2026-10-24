Guide: Running a script on the AMI dataset (Nautilus)

The AMI Corpus (meeting video, audio, and annotations) is stored on the PVC “abhati23-ami-dataset” in the aiea-auditors namespace. You can run your own scripts on it without copying the data. Your script runs in a small Job that mounts the PVC at /data.

Dataset layout

```
/data/amicorpus/<meetingID>/video/*.avi
/data/amicorpus/<meetingID>/audio/*.wav
/data/<annotation folders>   (words, segments, dialogueActs, ...)
/data/README.txt
```

Instructions

* Make sure you have kubectl set up and are in the aiea-auditors namespace
* Everything you create must start with your cruz id
* Don’t write to /data. Make it read only (my YAML below does this).

Step 1: Write your script. Save it as my_script.py. Read the data from /data.

Example script:

```python
import os
meetings = os.listdir("/data/amicorpus")
print(meetings)
```

Step 2: Store the script on the cluster

```
kubectl create configmap <cruzid>-my-script --from-file=my_script.py
```

Step 3: Create the Job file. Save this as `<cruzid>-my-job.yaml` and replace the two `<cruzid>` spots

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: <cruzid>-my-job
spec:
  backoffLimit: 0
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: run
        image: python:3.11-slim
        command: ["python", "/scripts/my_script.py"]
        resources:
          requests:
            cpu: 1
            memory: 1Gi
          limits:
            cpu: 1
            memory: 1Gi
        volumeMounts:
        - name: datasets
          mountPath: /data
          readOnly: true
        - name: script
          mountPath: /scripts
      volumes:
      - name: datasets
        persistentVolumeClaim:
          claimName: abhati23-ami-dataset
          readOnly: true
      - name: script
        configMap:
          name: <cruzid>-my-script
```

Step 4: Run it and read the output

```
kubectl create -f <cruzid>-my-job.yaml
kubectl get pods | grep <cruzid>
kubectl logs job/<cruzid>-my-job
```

Wait until the pod says Completed, then run logs to see what your script printed.

Step 5: Clean up. The Job deletes itself after an hour, but you can do this to remove it right away

```
kubectl delete job <cruzid>-my-job
kubectl delete configmap <cruzid>-my-script
```

To re-run after editing the script: delete the old job and configmap, then repeat steps 2 and 4.
