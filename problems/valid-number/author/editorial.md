# Private organizer reference: Valid Number

Scan an optional sign, mantissa digits, an optional decimal point and more mantissa digits. Require at least one mantissa digit. If an exponent appears, consume an optional sign and require exponent digits. Accept only if the entire string is consumed. Do not convert to a floating-point value: NaN/Infinity are invalid spellings, while a syntactically valid enormous exponent is allowed.

Time: {'Syntax scan': 'O(L)'}. Auxiliary space: O(1) auxiliary space. Include input/output storage and serialization when reviewing total space. The reference is not a required implementation.

Generate with `python author/generate_tests.py`; verify with the repository's function-problem verification tool. Saved samples have explicitly checked expected results. Random small cases use independent oracles; substring scale cases use known patterns.
