# GS1 DataMatrix Serialization Engine

    python main.py          # interactive: prompts for everything
    python -m unittest discover tests

No third-party dependencies (tests optionally use pylibdmtx + Pillow).

## Layout
    main.py                  entry point
    gs1/
      models.py              GS1Code dataclass (human + raw data stream)
      validation.py          GTIN check digit, expiry, batch, serial rules
      serials.py             first serial -> N unique serials
      batch.py               validated inputs -> list[GS1Code]
      datamatrix/
        tables.py            ECC200 symbol sizes
        galois.py            Reed-Solomon (GF(256))
        placement.py         module placement algorithm
        encoder.py           codewords + assembly -> module matrix
      png.py                 pure-Python PNG writer
      export.py              CSV + image output
      cli.py                 interactive prompts
    tests/test_engine.py
