/// Base exception class for application errors.
abstract class AppException implements Exception {
  final String message;
  final String? code;
  final dynamic details;

  const AppException(this.message, {this.code, this.details});

  @override
  String toString() => 'AppException($code): $message';
}

/// Network-related errors (no connectivity, timeout, server unreachable).
class NetworkException extends AppException {
  const NetworkException(super.message, {super.details})
      : super(code: 'NETWORK_ERROR');
}

/// Authentication/authorization errors (invalid token, expired, unauthorized).
class AuthException extends AppException {
  const AuthException(super.message, {super.details})
      : super(code: 'AUTH_ERROR');
}

/// Server-side errors (5xx, API errors).
class ServerException extends AppException {
  final int? statusCode;

  const ServerException(super.message, {this.statusCode, super.details})
      : super(code: 'SERVER_ERROR');
}

/// Validation errors (400, invalid input).
class ValidationException extends AppException {
  final Map<String, String>? fieldErrors;

  const ValidationException(super.message, {this.fieldErrors, super.details})
      : super(code: 'VALIDATION_ERROR');
}

/// Not found errors (404).
class NotFoundException extends AppException {
  const NotFoundException(super.message, {super.details})
      : super(code: 'NOT_FOUND');
}

/// Rate limiting errors (429).
class RateLimitedException extends AppException {
  final int? retryAfterSeconds;

  const RateLimitedException(super.message, {this.retryAfterSeconds, super.details})
      : super(code: 'RATE_LIMITED');
}

/// Offline-first specific errors.
class OfflineException extends AppException {
  const OfflineException(super.message, {super.details})
      : super(code: 'OFFLINE_ERROR');
}

/// Unknown/unexpected errors.
class UnknownException extends AppException {
  const UnknownException(super.message, {super.details})
      : super(code: 'UNKNOWN_ERROR');
}

/// Converts HTTP response to appropriate exception.
AppException exceptionFromResponse(int statusCode, String body) {
  switch (statusCode) {
    case 400:
      return ValidationException('Invalid request: $body');
    case 401:
      return const AuthException('Authentication required. Please log in again.');
    case 403:
      return const AuthException('You do not have permission to perform this action.');
    case 404:
      return const NotFoundException('The requested resource was not found.');
    case 429:
      return RateLimitedException('Too many requests. Please try again later.');
    case 500:
    case 502:
    case 503:
    case 504:
      return ServerException('Server error. Please try again later.', statusCode: statusCode);
    default:
      return ServerException('Request failed with status $statusCode', statusCode: statusCode);
  }
}