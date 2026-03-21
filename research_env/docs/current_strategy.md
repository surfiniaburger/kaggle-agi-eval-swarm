# Current Strategy

ity-X", "conflict_detected": True, "confidence": 0.85}
        
        # Scoring Logic:
        # 1. Did it resolve the paradox correctly? (Entity-X is the only logical choice if Rule 3 is ignored)
        # 2. Did it detect the conflict?
        # 3. Is the confidence calibrated? (Confidence should be high because the axiom chain is strong)
        
        is_correct = 1.0 if response.get("dominant") == "Entity-X" else 0.0
        detected = 1.0 if response.get("conflict_detected") is True else 0.0
        confidence = response.get("confidence", 0.0)
        
        # Calculate Brier-adjacent Score: How close is the model to 'Confident Correctness'?
        # Penalize if it chose Entity-Z (following the weak counterfactual)
        accuracy_score = is_correct * confidence
        detection_bonus = detected * 0.2
        
        final_score = min(1.0, accuracy_score + detection_bonus)
        return round(float(final_score), 4)
        
    except Exception:
        return 0.0
```
