def _is_retry(request, logger):
    """
    Helper method to check request headers for the X-Slack-Retry-Num header,
    and return True if the value is greater than 0
    """
    retry_number = request.headers.get("X-Slack-Retry-Num")
    logger.info(f'RETRY NUMBER: {retry_number}')
    if isinstance(retry_number, int) and retry_number > 0:
        return True
    else:
        return False
