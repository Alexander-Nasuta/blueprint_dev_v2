

def propagate_errors_via_broker(func):
    def wrapper(*args, **kwargs):
        try:
            # Execute the decorated function
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Print the exception if one occurs
            print(f"Exception in {func.__name__}: {e}")
            # Optionally, you can re-raise the exception if needed
            # raise

    return wrapper