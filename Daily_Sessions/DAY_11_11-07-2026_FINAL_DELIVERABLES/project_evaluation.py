def evaluate_project(accuracy, response_time_ms, features_completed):
    score = 0
    if accuracy > 0.90:
        score += 40
    if response_time_ms < 500:
        score += 30
    score += min(30, features_completed * 10)
    return score

final_score = evaluate_project(accuracy=0.95, response_time_ms=300, features_completed=4)
print(f"Final Project Evaluation Score: {final_score}/100")
print("Project ready for final presentation.")
