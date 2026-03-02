# Password Strength Estimator

Estimates password strength using a logistic regression model trained on real passwords, with extra checks for personal info (name, birthday).

**Live demo:** [password-strength-estimator-by-aryan-b.streamlit.app](https://password-strength-estimator-by-aryan-b.streamlit.app/)

## Scoring

| Score  | Label  |
|--------|--------|
| 0–60   | Weak   |
| 61–80  | OK     |
| 81–100 | Strong |

## Run Locally

```
pip install streamlit
streamlit run app.py
```
