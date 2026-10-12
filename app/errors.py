class EchoFlowError(Exception):
    """User-facing application error with a stable code."""

    def __init__(self, message: str, code: str = "error", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class AudioValidationError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="audio_validation", status_code=400)


class AudioProcessingError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="audio_processing", status_code=422)


class TranscriptionError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="transcription", status_code=500)


class ModelError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="model", status_code=500)


class DatabaseError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="database", status_code=500)


class DependencyError(EchoFlowError):
    def __init__(self, message: str):
        super().__init__(message, code="dependency", status_code=503)
