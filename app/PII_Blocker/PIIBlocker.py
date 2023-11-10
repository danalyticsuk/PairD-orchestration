import json
import scrubadub, scrubadub_spacy
from typing import Optional, Union
import re

import spacy_transformers

from ConfidentialityControl.UniqueDetector import UniqueDetector
from ConfidentialityControl.WhitelistScrubber import WhitelistScrubber

class PIIBlocker(object):
    """
    Blocker for personally identifiable information (PII).

    Removes or masks information that could be used to identify persons,
    entities, and other bodies and risk identity theft or confidentiality
    breaches.

    Parameters
    ----------
    strategy : {"remove", "mask"}, default="mask"
        Configure the strategy used to block PII.

        - `"remove"`: Strips PII entirely from the source document(s)
        - `"mask"`: Replaces PII with placeholder values

    deterministic : bool, default=True
        Whether replacements of PII will have a one-to-one mapping with named
        entities. Only applies if `strategy` is `"mask"`.

    strength : {"weak", "moderate", "strong"} or None, default="strong"
        How strong blocking of PII will be.

        - None: Filters nothing by default. Add detectors via the
          `add_detectors()` method
        - `"weak"`: Only replaces phone numbers, emails, passport numbers,
          license numbers, credit card numbers, and social security numbers.
        - `"moderate"`: Replaces phone numbers, and emails. Replaces surnames
          and dates of birth.
        - `"strong"`: Replaces anything that could be considered PII.

    locale : string, default="en_GB"
        International locale code to use for the language within named entity
        recognition.

    add_detectors : list of string or None, default=None
        List of detectors to add (on top of defaults chosen by `strength`).
        Refer to documentation for list of supported detectors.

    remove_detectors : list of string or None, default=None
        List of detectors to remove (on top of defaults chosen by `strength`).
        Refer to documentation for list of supported detectors.

    blacklist : list of dict or None, default=None
        Blacklisted PII to remove or mask. Must be a string pointing to a JSON
        file, or a Python object. The input must be a list of dictionary
        objects with required keys:
        
        - `pii`: str. PII to match/block.
        - `type`: str. Type of PII (e.g. 'name', 'postalcode', etc.). Currently
          only supports scrubadub PII names.
        
        Optionally, the following keys can be present:

        - `ignore_case`: bool, default=True. Whether PII detection will rely
        on case of `pii`.

    whitelist : list of string or list of dict or None, default=None
        List of whitelisted PII to allow. If specified as a list of strings,
        assume that case is not ignored when scanning for whitelisted PII (e.g.
        if 'abcd' is whitelisted, 'abCd' will still be blocked.)

        Optionally the user can specify cases to ignore, in which a list of
        dictionary objects should be provided with the keys:

        - `pii`: str. PII to match and allow.
        - `ignore_case`: bool. Whether to ignore case when matching `pii`.
    """
    def __init__(self,
                 strategy: str="mask",
                 deterministic: bool=True,
                 strength: str | None ="strong",
                 locale: str="en_GB",
                 add_detectors: Optional[list[str]] = None,
                 remove_detectors: Optional[list[str]] = None,
                 blacklist: Optional[Union[str, list[dict]]] = None,
                 whitelist: Optional[list[str]] = None) -> None:
        self.strategy = strategy
        self.deterministic = deterministic
        self.strength = strength
        self.locale = locale
        self.spacy_entities = {'spacy_gpe': 'GPE', 'spacy_org': 'ORG'}

        self._replacement_dict = {}

        if add_detectors is None:
            add_detectors = []
        if remove_detectors is None:
            remove_detectors = []

        
        # mask or remove depending on strategy
        match strategy:
            case "mask":
                post_processor_list=[
                    scrubadub.post_processors.FilthReplacer(
                        include_type=True, include_count=deterministic
                    ),
                    scrubadub.post_processors.PrefixSuffixReplacer(
                        prefix="[", suffix="]"
                    ),
                ]
                locale=locale

            case "remove":
                post_processor_list=[
                    scrubadub.post_processors.remover.FilthRemover(),
                ]
                locale=locale

            case _:
                raise ValueError("Strategy must be one of ['mask', 'remove']")

        self._scrubber = WhitelistScrubber(
            whitelist=whitelist,
            post_processor_list=post_processor_list,
            locale=locale,
            detector_list=[] if strength is None else None,
        )


        # Handle the addition of SpaCy scrubbers separately due to it containtain multiple scrubbers in one detector
        spacy_entities_to_add = [spacy_detector for spacy_detector in add_detectors if spacy_detector.startswith('spacy_')]
        add_ent = [self.spacy_entities[i] for i in spacy_entities_to_add]

        self._scrubber.add_detector(scrubadub_spacy.detectors.spacy.SpacyEntityDetector(named_entities=add_ent))



        # Find detectors to remove depending on strength
        to_remove = []
        entities = set()
        match strength:
            case "weak":
                to_remove = [
                    "email", "phone", "postalcode", "twitter", "url",
                ]
            case "moderate":
                to_remove = ["email", "postalcode", "url"]
                entities = {"PER"} # TODO: should we exclude person names?
            case "strong":
                entities = {"PERSON", "PER", "ORG"}
            case None:
                pass
            case _:
                raise ValueError("Strength must be one of ['weak', 'moderate', 'strong']")

        # Remove detectors
        for detector in set(to_remove).union(set(remove_detectors)):
            # TODO: figure out better way of doing this
            if detector == "name":
                entities = entities.difference({"PERSON", "PER"})
                continue
            elif detector == "org":
                entities = entities.difference({"ORG"})
                continue

            try:
                self._scrubber.remove_detector(detector)
            except KeyError as e:
                # TODO: we need to document these
                raise KeyError(f"Could not find detector {detector} to remove. Ensure this is a supported detector. Original error message: {e}")




        # Add any remaining detectors
        for detector in set(add_detectors).difference(set([k for k in self._scrubber._detectors.keys()])):
            if detector == "name":
                entities = entities.union({"PERSON", "PER"})
                continue
            elif detector == "org":
                entities = entities.union({"ORG"})
                continue

            try:
                # Handle detectors otherthan from SpaCy
                if not detector.startswith('spacy_'):       
                    print("Adding detector", detector)
                    self._scrubber.add_detector(detector)
            except KeyError as e:
                # TODO: we need to document these
                raise KeyError(f"'{detector}' is not a supported detector. The available detectors are: {scrubadub.detectors.detector_catalogue.get_all()}. {e}")

        # Add blacklist
        if blacklist is not None:
            if isinstance(blacklist, list):
                # List of dictionaries in the right format
                contents = blacklist

            elif isinstance(blacklist, str):
                # Read the blacklist as a JSON file
                with open(blacklist, "r") as file:
                    contents = json.load(file)
                    contents = contents["blacklist"]

            else:
                raise TypeError(f"`blacklist` must be list[dict] or str object.")

            self._set_blacklist(contents)



        

    def _set_blacklist(self, blacklist: list[dict]):
        blacklist_filter = []
        for filth in blacklist:
            try:
                if filth["pii"] not in self._scrubber._detectors:
                    self._scrubber.add_detector(
                        UniqueDetector(pii=filth["pii"],
                                       type=filth["type"],
                                       locale=self.locale,
                                       ignore_case=filth.get("ignore_case", False))
                    )

                else:
                    blacklist_filter.extend([{"match": filth["pii"],
                                            "filth_type": filth["type"],
                                            "ignore_case": filth.get(
                                                "ignore_case", True
                                            )}]
                                            )
                    
            except KeyError as e:
                raise KeyError(f"Ensure items in the `blacklist` have 'pii' and 'type' at a minimum: {e}")

        # Remove if a blacklist already exists
        if 'user_supplied' in self._scrubber._detectors:
            self._scrubber.remove_detector('user_supplied')

        self._scrubber.add_detector(
            scrubadub.detectors.UserSuppliedFilthDetector(
                blacklist_filter
            )
        )

    
    def _update_whitelist(self, new_whitelist):
        self._scrubber.whitelist = self._scrubber._update_whitelist(
            new_whitelist
        )


    def remask(self, text):
        """Naively add PII back to blocked string.

        Replaces instances of masks with corresponding PII. Only available for
        deterministic masking and if strategy='mask'.

        Parameters
        ----------
        text : string
            Text to susbtitute with PII.

        Returns
        -------
        new_text : string
            Text with re-masked PII."""
        # NOTE: this is a naive strategy, but there isn't any better way I can
        # think of.
        if self.strategy == "remove" or not self.deterministic:
            return text
        pii_pattern = r"\[[A-Z]+\-\d+\]"
        
        def replace_with_dict(match):
            matched_string = match.group(0)
            return self._scrubber._filth_to_clean.get(matched_string, matched_string)

        return re.sub(pii_pattern, replace_with_dict, text)


    def block(self, text):
        """Block PII within a string.

        Parameters
        ----------
        text : string
            Text to apply the PII blocker to.

        Returns
        -------
        new_text : string
            Scrubbed/cleaned text in the same shape as `text`.
        """
        return self._scrubber.clean(text)
    

    def get_pii(self, prompt) -> list[Union[str, bool]]:
        """Get the list of PII from a user prompt.

        Returns PII in shape [[text: str, type: str, blocked/allowed: bool]].

        Parameters
        ----------
        prompt : string or array-like of string
            Text to apply the PII blocker to.

        Returns
        -------
        detectedPII : list of strings
            Extracted words/phrases deemed to be PII. detectedPII includes True bool to allow users to enable/disable the PII
        """
        FilthReplacer = scrubadub.post_processors.FilthReplacer(include_type=True, include_count=self.deterministic)
        detectedPII = []
        
        for filth in self._scrubber.iter_filth(prompt):
            detectedPII.append([filth.text ,("["+FilthReplacer.filth_label(filth)+"]"), True])

        return detectedPII
