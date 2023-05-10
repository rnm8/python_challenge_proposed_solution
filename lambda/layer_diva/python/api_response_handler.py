from dataclasses import dataclass
import json
from aws_lambda_powertools import Logger
from response import ApiGwResponse
class NotFoundError(Exception):
    pass

class BadRequest(Exception):
    pass

class Unauthorized(Exception):
    pass

class Forbidden(Exception):
    pass

log = Logger()

def api_response_handler(func):
    def wrapper(event, context, **kwargs):
        try:
            return ApiGwResponse(200, func(event, context, **kwargs)).to_json()
        except BadRequest as e:
            log.warning(e)
            return ApiGwResponse(400, str(e)).to_json()
        except Unauthorized as e:
            log.warning(e)
            return ApiGwResponse(401).to_json()
        except Forbidden as e:
            log.warning(e)
            return ApiGwResponse(403).to_json()
        except NotFoundError as e:
            log.warning(e)
            return ApiGwResponse(404).to_json()
        except Exception as e:
            log.exception(e)
            return ApiGwResponse(500).to_json()
    
    return wrapper

