import json
import os
import threading

from common.v1 import trans_pb2
from grpc import StatusCode

from utils.app_error import AppError


class TransManager():
  _instance = None
  _lock = threading.Lock()
  _translations: dict[str, trans_pb2.TranslationElements] = {}

  def __new__(cls):
    if cls._instance is None:
      with cls._lock:
        # ensures that no two threads create the instance during race conditions.
        if cls._instance is None:
          cls._instance = super(TransManager, cls).__new__(cls)
          cls._instance._load_translations("i18n")

    return cls._instance

  def _load_translations(self, dir: str):
    for fn in os.listdir(dir):
      if fn.endswith(".json"):
        lang_code = fn.replace(".json", "")
        fp = os.path.join(dir, fn)
        try:
          with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
            elements = []
            for t in data:
              el = trans_pb2.TranslationElement(id=t["id"], tr=t["tr"])
              elements.append(el)
            tr = trans_pb2.TranslationElements(trans=elements)
            self._translations[lang_code] = tr

        except (json.JSONDecodeError, OSError) as err:
          sc = StatusCode.INTERNAL.value[0]
          raise AppError(
              where="common.trans._load_translations",
              id="common.trans.load_trans.internal",
              status_code=sc,
              detailed_error=f"failed to load filename: {fn}, err: {err}",
          )

  def get_translation_for_lang(self, lang: str):
    res = self._translations.get(lang)
    if res is None:
      sc = StatusCode.NOT_FOUND.value[0]
      e = AppError(
          where="common.trans.get_translations_for_lang",
          id="common.trans.get.not_found",
          status_code=sc,
          detailed_error=
          f"the requested lang: {lang} is not found. please make sure to see the supported languages",
      )
      return trans_pb2.TranslationsForLangGetResponse(error=e)
    return trans_pb2.TranslationsForLangGetResponse(data=res)

  def get_translations(self):
    print(self._translations)
    data_msg = trans_pb2.TranslationsGetResponse()
    for lang, elements in self._translations.items():
      data_msg.data[lang].CopyFrom(elements)
    return data_msg
