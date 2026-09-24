OFFLINE_MODE = True

RISK_THRESHOLDS = {
    "allow": 30,
    "monitor": 60,
    "approval": 80
}

RISK_WEIGHTS = {
    "threat": 25,
    "data": 25,
    "permission": 25,
    "action": 25
}

PROTECTED_RESOURCES = [
    "system",
    "production",
    "database",
    "credentials",
    "secrets",
    "customer_data"
]