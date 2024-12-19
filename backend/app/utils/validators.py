# Checks if selected tests are in available
def validate_tests(tests: list, available_tests: list):
    for test in tests:
        if test not in available_tests:
            # raise ValueError(f"Invalid test selected: {test}")
            raise HTTPException(status_code=400, detail=f"Invalid test selected: {test}")