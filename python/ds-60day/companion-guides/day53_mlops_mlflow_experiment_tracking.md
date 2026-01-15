# Day 53 — MLOps: MLflow Experiment Tracking (Companion Guide)

## Learning objectives
- Track params, metrics, artifacts, and models with MLflow
- Run the tracking UI and compare runs
- Use autologging and the Model Registry (concepts)

## Why this matters
Reproducibility and comparability are essential for iterative modeling.

## Core concepts and examples
### Basic logging
```python
import mlflow
mlflow.set_experiment('churn-baseline')
with mlflow.start_run():
    mlflow.log_params({'model':'rf','n_estimators':300})
    mlflow.log_metric('auc', 0.812)
    mlflow.sklearn.log_model(clf, 'model')
```

### UI
- `mlflow ui --port 5000` and open http://localhost:5000

### Autologging
```python
mlflow.sklearn.autolog()
```

## Common pitfalls
- Logging outside a run context; nothing gets recorded
- Not pinning versions; runs become irreproducible
- Sensitive data in artifacts; sanitize before logging

## Practice exercises
1) Track a grid search with MLflow and compare runs
2) Save the best model as an artifact and load it elsewhere
3) Explore Model Registry concepts

## Further reading
- MLflow: https://mlflow.org
