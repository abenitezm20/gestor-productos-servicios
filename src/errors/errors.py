class ApiError(Exception):
    code = 500
    description = "internal_server_error"


class BadRequest(ApiError):
    code = 400
    description = "bad_request"


class Unauthorized(ApiError):
    code = 401
    description = "unauthorized"


class Forbidden(ApiError):
    code = 403
    description = "forbidden"


class TokenNotFound(ApiError):
    code = 403
    description = "token_not_found"


class ResourceNotFound(ApiError):
    code = 404
    description = "resource_not_found"


class PreconditionFailed(ApiError):
    code = 412
    description = "precondition_failed"


class UserAlreadyExist(ApiError):
    code = 432
    description = "user_already_exists"