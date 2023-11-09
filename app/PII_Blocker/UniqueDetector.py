import re
import scrubadub, scrubadub_spacy
from scrubadub.scrubbers import Generator
from typing import Optional
from scrubadub import Filth

class UniqueDetector(scrubadub.detectors.Detector):
    def __init__(self, 
                 pii: str,
                 type: str,
                 locale: str,
                 ignore_case: bool = False):
        self.pii = pii
        self.type = type
        self.locale = locale
        
        self.name = f"User-defined detector for '{pii}'"
        if ignore_case:
            self.regex = re.compile(self.pii+"?", re.IGNORECASE)
        else:
            self.regex = re.compile(self.pii+"?")

        class UniqueType(scrubadub.filth.Filth):
            type = self.type

        self.filth_cls = UniqueType

    def iter_filth(self, text: str, document_name: Optional[str] = None) -> Generator[Filth, None, None]:
            for match in self.regex.finditer(text):
                yield self.filth_cls(match=match, detector_name=self.name, document_name=document_name,
                                     locale=self.locale)