import scrubadub
from typing import Optional, Union
from scrubadub import Sequence, Filth


class WhitelistScrubber(scrubadub.Scrubber):
    def __init__(self,
                 whitelist: Optional[Union[list[str],list[dict[str,Union[str,bool]]]]] = None,
                 **kwargs):
        super(WhitelistScrubber, self).__init__(**kwargs)

        # Initialize whitelist to be { pii.lower() : (pii, ignore_case) }
        self.whitelist = self._update_whitelist(whitelist)
        self._filth_to_clean = {}


    def _update_whitelist(self, whitelist):
        new_whitelist = dict()
        
        if whitelist is None or whitelist == []:
            pass
        elif isinstance(whitelist[0], str):
            # Convert list of strs to dict of (pii : ignore_case)
            new_whitelist = {filth.lower() : (filth, False) for filth in whitelist}
        elif isinstance(whitelist[0], dict):
            try:
                new_whitelist = {filth['pii'].lower() : (filth['pii'], filth['ignore_case']) for filth in whitelist}
            except KeyError as e:
                raise KeyError(f"Could not find `pii` or `ignore_case` in whitelist dictionary: {e}")
        else:
            raise TypeError(f"`whitelist` must be of type None, list[str], or dict[str, str|bool].")

        return new_whitelist

    def _replace_text(self, text: str, filth_list: Sequence[Filth], document_name: Optional[str], **kwargs) -> str:
        filth_list = [filth for filth in filth_list if filth.document_name == document_name]
        if len(filth_list) == 0:
            return text

        def replace_next_filth(next_filth, clean_chunks):
            if next_filth.replacement_string is not None:
                clean_chunks.append(next_filth.replacement_string)
            else:
                clean_chunks.append(next_filth.replace_with(**kwargs))
            if clean_chunks[-1] not in self._filth_to_clean:
                self._filth_to_clean[clean_chunks[-1]] = next_filth.text

        filth_list = self._sort_filths(filth_list)
        filth = None
        clean_chunks = []
        for next_filth in filth_list:
            clean_chunks.append(text[(0 if filth is None else filth.end):next_filth.beg])
            (original_pii, ignore_case) = self.whitelist.get(next_filth.text.lower(), (None, None))

            if ignore_case is None:
                # Filth is not whitelisted
                replace_next_filth(next_filth, clean_chunks)
            elif ignore_case:
                # We ignore case, so just add the original filth
                clean_chunks.append(next_filth.text)
            else:
                # We need to ensure filth case == whitelist case to not block
                if next_filth.text != original_pii:
                    replace_next_filth(next_filth, clean_chunks)
                else:
                    clean_chunks.append(next_filth.text)
            filth = next_filth
        if filth is not None:
            clean_chunks.append(text[filth.end:])
        return u''.join(clean_chunks)

