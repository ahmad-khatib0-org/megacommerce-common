import json
from typing import Dict, Optional

from shared.v1.error_pb2 import AppError as AppErrorProto

from types_lib.general import translate_func
from utils.constants import MAX_ERROR_LENGTH


class AppError(Exception):
  def __init__(
      self,
      where: str,
      id: str,
      params: Optional[Dict[str, str]] = None,
      detailed_error: str = "",
      status_code: int = 0,
      skip_translation: bool = False,
      wrapped: Optional[Exception] = None,
  ) -> None:
    self.id = id
    self.message = id  # will be overwritten if translated
    self.detailed_error = detailed_error
    self.request_id = ""
    self.status_code = status_code
    self.where = where
    self.skip_translation = skip_translation
    self.params = params or {}
    self.wrapped = wrapped
    self.translate()

  def __str__(self) -> str:
    parts = [f"{self.where}: {self.message}"]
    if self.detailed_error:
      parts.append(self.detailed_error)
    if self.wrapped:
      parts.append(str(self.wrapped))
    result = ", ".join(parts)
    return result[:MAX_ERROR_LENGTH] + "..." if len(result) > MAX_ERROR_LENGTH else result

  def translate(self, tr: Optional[translate_func] = None):
    if self.skip_translation:
      return

    if tr is None:
      self.message = self.id
      return

    else:
      self.message = tr(self.id, "")

  def to_json(self):
    return json.dumps({
        "id": self.id,
        "message": self.message,
        "detailed_error": self.detailed_error,
        "request_id": self.request_id,
        "status_code": self.status_code,
        "where": self.where,
        "skip_translation": self.skip_translation,
        "params": self.params,
    })

  def to_proto(self):
    return AppErrorProto(
        id=self.id,
        message=self.message,
        detailed_error=self.detailed_error,
        request_id=self.request_id,
        status_code=self.status_code,
        where=self.where,
        skip_translation=self.skip_translation,
        params=self.params,
    )
